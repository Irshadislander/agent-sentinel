from __future__ import annotations

import hashlib
import ipaddress
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Literal
from urllib.parse import urlparse

from agent_sentinel.security.audit import AuditEvent, from_exception, make_event
from agent_sentinel.security.capabilities import (
    FS_READ_PRIVATE,
    FS_READ_PUBLIC,
    FS_WRITE_WORKSPACE,
    NET_EXTERNAL,
    NET_HTTP_GET,
    NET_HTTP_POST,
    NET_INTERNAL,
    is_known,
)
from agent_sentinel.security.context import RequestContext, new_request_id
from agent_sentinel.security.errors import (
    AgentSentinelError,
    InvalidPolicyFormatError,
    PolicyViolationError,
    UnknownCapabilityError,
)

ALLOW = "ALLOW"
DENY = "DENY"
REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
ALLOW_WITH_REDACTION = "ALLOW_WITH_REDACTION"

RULE_ALLOW_MATCH = "RULE_ALLOW_MATCH"
RULE_DENY_MATCH = "RULE_DENY_MATCH"
DEFAULT_DENY_NO_MATCH = "DEFAULT_DENY_NO_MATCH"
POLICY_INVALID = "POLICY_INVALID"
POLICY_MISSING = "POLICY_MISSING"

_SENSITIVE_TOKENS = ("email", "token", "secret", "password")
_HTTP_GET_NAMES = {"http.get", "http_get", "tools.http.get", "http_tool.http_get"}
_HTTP_POST_NAMES = {"http.post", "http_post", "tools.http.post", "http_tool.http_post"}
_FS_READ_NAMES = {"fs.read", "fs.read_text", "read_text", "fs_tool.read_text"}
_FS_WRITE_NAMES = {"fs.write", "fs.write_text", "write_text", "fs_tool.write_text"}


@dataclass(frozen=True, slots=True)
class DecisionResult:
    decision: Literal["allow", "deny"]
    rule_id: str | None
    reason_code: str
    evaluation_trace: list[str]
    duration_ms: float
    trace_commitment: str | None = None


@dataclass(frozen=True)
class _CapabilityRule:
    rule_id: str
    action: Literal["allow", "deny"]
    capabilities: tuple[str, ...]


def _extract_allowlist(policy: Any) -> list[str]:
    if not isinstance(policy, dict):
        raise InvalidPolicyFormatError("Policy must be a dict.")

    if "allow" not in policy:
        raise InvalidPolicyFormatError("Missing required key: 'allow'.")

    allow = policy["allow"]
    if not isinstance(allow, list):
        raise InvalidPolicyFormatError("'allow' must be a list of strings.")

    if not all(isinstance(x, str) for x in allow):
        raise InvalidPolicyFormatError("'allow' must contain only strings.")

    return allow


def _extract_rules(policy: Any) -> tuple[_CapabilityRule, ...]:
    if not isinstance(policy, dict):
        raise InvalidPolicyFormatError("Policy must be a dict.")

    if "rules" in policy:
        raw_rules = policy["rules"]
        if not isinstance(raw_rules, list):
            raise InvalidPolicyFormatError("'rules' must be a list.")

        rules: list[_CapabilityRule] = []
        seen_rule_ids: set[str] = set()
        for index, raw_rule in enumerate(raw_rules):
            if not isinstance(raw_rule, dict):
                raise InvalidPolicyFormatError(f"'rules[{index}]' must be an object.")

            rule_id_value = raw_rule.get("rule_id")
            if not isinstance(rule_id_value, str) or not rule_id_value:
                raise InvalidPolicyFormatError(
                    f"'rules[{index}].rule_id' must be a non-empty string."
                )
            if rule_id_value in seen_rule_ids:
                raise InvalidPolicyFormatError(f"duplicate rule_id: {rule_id_value}")
            seen_rule_ids.add(rule_id_value)

            action_value = raw_rule.get("action")
            if action_value not in {"allow", "deny"}:
                raise InvalidPolicyFormatError(
                    f"'rules[{index}].action' must be 'allow' or 'deny'."
                )

            capabilities_value = raw_rule.get("capabilities")
            if not isinstance(capabilities_value, list) or not all(
                isinstance(capability, str) for capability in capabilities_value
            ):
                raise InvalidPolicyFormatError(
                    f"'rules[{index}].capabilities' must be a list of strings."
                )

            rules.append(
                _CapabilityRule(
                    rule_id=rule_id_value,
                    action=action_value,
                    capabilities=tuple(capabilities_value),
                )
            )
        return tuple(rules)

    allow = _extract_allowlist(policy)
    return tuple(
        _CapabilityRule(
            rule_id=f"allow_{index:03d}",
            action="allow",
            capabilities=(capability,),
        )
        for index, capability in enumerate(allow)
    )


def _allowed_capabilities_from_policy(policy: Any) -> list[str]:
    try:
        rules = _extract_rules(policy)
    except InvalidPolicyFormatError:
        return []

    allowed_caps: list[str] = []
    for rule in rules:
        if rule.action != "allow":
            continue
        for capability in rule.capabilities:
            if capability not in allowed_caps:
                allowed_caps.append(capability)
    return allowed_caps


def _build_result(
    *,
    start_time: float,
    decision: Literal["allow", "deny"],
    rule_id: str | None,
    reason_code: str,
    evaluation_trace: list[str],
    trace_commitment: str | None,
) -> DecisionResult:
    return DecisionResult(
        decision=decision,
        rule_id=rule_id,
        reason_code=reason_code,
        evaluation_trace=evaluation_trace,
        duration_ms=(time.perf_counter() - start_time) * 1000.0,
        trace_commitment=trace_commitment,
    )


def _trace_integrity_enabled(policy: Any) -> bool:
    return isinstance(policy, dict) and bool(policy.get("trace_integrity", False))


def compute_trace_commitment(evaluation_trace: list[str]) -> str:
    """
    Compute a deterministic hash-chain commitment for an evaluation trace.

    trace_hash[i] = H(trace_hash[i-1] || trace_entry[i]), with a fixed zero seed.
    """

    previous = "0" * 64
    for entry in evaluation_trace:
        payload = f"{previous}|{entry}".encode()
        previous = hashlib.sha256(payload).hexdigest()
    return previous


def verify_trace_commitment(evaluation_trace: list[str], commitment: str | None) -> bool:
    if not commitment:
        return False
    return compute_trace_commitment(evaluation_trace) == commitment


def _trace_commitment(
    evaluation_trace: list[str],
    *,
    enabled: bool,
) -> str | None:
    if not enabled:
        return None
    return compute_trace_commitment(evaluation_trace)


def resolve_decision(
    capability: str,
    policy: Any,
    *,
    context: dict[str, Any] | None = None,
) -> DecisionResult:
    del context  # Reserved for future predicate context expansion.

    start = time.perf_counter()
    trace: list[str] = []
    integrity_enabled = _trace_integrity_enabled(policy)

    if policy is None:
        trace.append("policy:missing")
        trace.append(f"final:deny:{POLICY_MISSING}")
        return _build_result(
            start_time=start,
            decision="deny",
            rule_id=None,
            reason_code=POLICY_MISSING,
            evaluation_trace=trace,
            trace_commitment=_trace_commitment(trace, enabled=integrity_enabled),
        )

    try:
        rules = _extract_rules(policy)
    except InvalidPolicyFormatError:
        trace.append("policy:invalid")
        trace.append(f"final:deny:{POLICY_INVALID}")
        return _build_result(
            start_time=start,
            decision="deny",
            rule_id=None,
            reason_code=POLICY_INVALID,
            evaluation_trace=trace,
            trace_commitment=_trace_commitment(trace, enabled=integrity_enabled),
        )

    for rule in rules:
        trace.append(f"eval:{rule.rule_id}")
        if capability not in rule.capabilities:
            continue

        trace.append(f"match:{rule.rule_id}:{rule.action}")
        reason_code = RULE_ALLOW_MATCH if rule.action == "allow" else RULE_DENY_MATCH
        trace.append(f"final:{rule.action}:{reason_code}")
        return _build_result(
            start_time=start,
            decision=rule.action,
            rule_id=rule.rule_id,
            reason_code=reason_code,
            evaluation_trace=trace,
            trace_commitment=_trace_commitment(trace, enabled=integrity_enabled),
        )

    trace.append("no_match")
    trace.append(f"final:deny:{DEFAULT_DENY_NO_MATCH}")
    return _build_result(
        start_time=start,
        decision="deny",
        rule_id=None,
        reason_code=DEFAULT_DENY_NO_MATCH,
        evaluation_trace=trace,
        trace_commitment=_trace_commitment(trace, enabled=integrity_enabled),
    )


def _raise_for_denied_result(capability: str, policy: Any, result: DecisionResult) -> None:
    reason_with_rule = result.reason_code
    if result.rule_id is not None:
        reason_with_rule = f"{result.reason_code} (rule_id={result.rule_id})"

    if result.reason_code in {POLICY_INVALID, POLICY_MISSING}:
        raise InvalidPolicyFormatError(reason_with_rule)

    allowed_capabilities = _allowed_capabilities_from_policy(policy)
    raise PolicyViolationError(
        requested_capability=capability,
        allowed_capabilities=allowed_capabilities,
        reason=reason_with_rule,
    )


def enforce(capability: str, policy: Any) -> None:
    """
    Enforce allowlist-only policy.
    Raises structured errors instead of returning bool.
    """
    if not is_known(capability):
        raise UnknownCapabilityError(capability)

    result = resolve_decision(capability, policy)
    if result.decision == "allow":
        return

    _raise_for_denied_result(capability, policy, result)


def enforce_request(
    capability: str,
    policy: Any,
    *,
    ctx: RequestContext | None = None,
    audit_sink: Callable[[AuditEvent], None] | None = None,
) -> None:
    effective_ctx = ctx or RequestContext(
        request_id=new_request_id(),
        correlation_id=None,
        source="cli",
    )

    if not is_known(capability):
        exc = UnknownCapabilityError(capability)
        if audit_sink is not None:
            audit_sink(from_exception(exc, ctx=effective_ctx, capability=capability))
        raise exc

    result = resolve_decision(capability, policy)
    if result.decision == "allow":
        if audit_sink is not None:
            audit_sink(
                make_event(
                    ctx=effective_ctx,
                    capability=capability,
                    decision="allow",
                    reason="capability allowed by policy",
                    rule_id=result.rule_id,
                    reason_code=result.reason_code,
                    duration_ms=result.duration_ms,
                    trace_len=len(result.evaluation_trace),
                    trace_commitment=result.trace_commitment,
                )
            )
        return

    if audit_sink is not None:
        reason = "InvalidPolicyFormatError"
        allowed_capabilities: list[str] | None = None
        if result.reason_code not in {POLICY_INVALID, POLICY_MISSING}:
            reason = "PolicyViolationError"
            allowed_capabilities = _allowed_capabilities_from_policy(policy)
        audit_sink(
            make_event(
                ctx=effective_ctx,
                capability=capability,
                decision="deny",
                reason=reason,
                allowed_capabilities=allowed_capabilities,
                rule_id=result.rule_id,
                reason_code=result.reason_code,
                duration_ms=result.duration_ms,
                trace_len=len(result.evaluation_trace),
                trace_commitment=result.trace_commitment,
            )
        )

    _raise_for_denied_result(capability, policy, result)


def is_allowed(capability: str, policy: Any) -> bool:
    """
    Backward-compatible bool API.
    """
    try:
        enforce(capability, policy)
        return True
    except AgentSentinelError:
        return False


@dataclass(slots=True)
class PolicyDecision:
    verdict: str
    reason: str
    redactions: dict[str, Any] | None = None


class PolicyEngine:
    def __init__(self, policy: dict[str, Any] | None):
        self._policy = policy or {}
        internal_domains = self._policy.get("internal_domains", ())
        self._internal_domains = tuple(
            str(domain).lower().lstrip(".") for domain in internal_domains
        )

    def decide(self, *, tool_name: str, args: dict[str, Any], caps: set[str]) -> PolicyDecision:
        normalized_tool = tool_name.strip().lower()

        if self._is_http_get(normalized_tool):
            return self._decide_http(method="GET", args=args, caps=caps)
        if self._is_http_post(normalized_tool):
            return self._decide_http(method="POST", args=args, caps=caps)
        if self._is_fs_read(normalized_tool):
            return self._decide_fs_read(args=args, caps=caps)
        if self._is_fs_write(normalized_tool):
            return self._decide_fs_write(args=args, caps=caps)

        return PolicyDecision(DENY, f"unknown tool denied by default: {tool_name}")

    def _decide_http(self, *, method: str, args: dict[str, Any], caps: set[str]) -> PolicyDecision:
        url = args.get("url")
        if not isinstance(url, str) or not url:
            return PolicyDecision(DENY, "missing required http url")

        if method == "GET" and NET_HTTP_GET not in caps:
            return PolicyDecision(DENY, f"{method} denied: missing capability {NET_HTTP_GET}")
        if method == "POST" and NET_HTTP_POST not in caps:
            return PolicyDecision(DENY, f"{method} denied: missing capability {NET_HTTP_POST}")

        is_external = self._is_external_destination(url)
        if is_external and NET_EXTERNAL not in caps:
            return PolicyDecision(
                DENY, f"{method} denied: external network requires {NET_EXTERNAL}"
            )
        if not is_external and NET_INTERNAL not in caps:
            return PolicyDecision(
                DENY, f"{method} denied: internal network requires {NET_INTERNAL}"
            )

        if is_external and self._contains_sensitive_key(args):
            return PolicyDecision(
                REQUIRE_APPROVAL,
                "external destination with sensitive payload requires explicit approval",
            )

        return self._allow_or_redact(args=args, reason=f"{method} allowed by policy")

    def _decide_fs_read(self, *, args: dict[str, Any], caps: set[str]) -> PolicyDecision:
        scope = self._path_scope(args.get("path"))
        if scope == "public":
            if FS_READ_PUBLIC in caps:
                return self._allow_or_redact(
                    args=args,
                    reason=f"file read allowed under public/ with {FS_READ_PUBLIC}",
                )
            return PolicyDecision(DENY, f"file read denied: missing capability {FS_READ_PUBLIC}")
        if scope == "private":
            if FS_READ_PRIVATE in caps:
                return self._allow_or_redact(
                    args=args,
                    reason=f"file read allowed under private/ with {FS_READ_PRIVATE}",
                )
            return PolicyDecision(DENY, f"file read denied: missing capability {FS_READ_PRIVATE}")
        if scope == "invalid":
            return PolicyDecision(DENY, "file read denied: invalid path")
        return PolicyDecision(DENY, "file read denied: path must be under public/ or private/")

    def _decide_fs_write(self, *, args: dict[str, Any], caps: set[str]) -> PolicyDecision:
        scope = self._path_scope(args.get("path"))
        if scope == "workspace":
            if FS_WRITE_WORKSPACE in caps:
                return self._allow_or_redact(
                    args=args,
                    reason=f"file write allowed under workspace/ with {FS_WRITE_WORKSPACE}",
                )
            return PolicyDecision(
                DENY, f"file write denied: missing capability {FS_WRITE_WORKSPACE}"
            )
        if scope == "invalid":
            return PolicyDecision(DENY, "file write denied: invalid path")
        return PolicyDecision(DENY, "file write denied: only workspace/ is writable")

    @staticmethod
    def _is_http_get(tool_name: str) -> bool:
        return tool_name in _HTTP_GET_NAMES

    @staticmethod
    def _is_http_post(tool_name: str) -> bool:
        return tool_name in _HTTP_POST_NAMES

    @staticmethod
    def _is_fs_read(tool_name: str) -> bool:
        return tool_name in _FS_READ_NAMES

    @staticmethod
    def _is_fs_write(tool_name: str) -> bool:
        return tool_name in _FS_WRITE_NAMES

    def _is_external_destination(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return True

        host = (parsed.hostname or "").lower()
        if not host:
            return True
        if host == "localhost" or host.endswith(".local") or host.endswith(".internal"):
            return False
        if self._is_internal_domain(host):
            return False

        try:
            ip = ipaddress.ip_address(host)
        except ValueError:
            return True

        return not (ip.is_loopback or ip.is_private or ip.is_link_local)

    def _is_internal_domain(self, host: str) -> bool:
        for domain in self._internal_domains:
            if host == domain or host.endswith(f".{domain}"):
                return True
        return False

    @staticmethod
    def _contains_sensitive_key(value: Any) -> bool:
        if isinstance(value, dict):
            for key, nested in value.items():
                lowered = str(key).lower()
                if any(token in lowered for token in _SENSITIVE_TOKENS):
                    return True
                if PolicyEngine._contains_sensitive_key(nested):
                    return True
            return False
        if isinstance(value, list):
            return any(PolicyEngine._contains_sensitive_key(item) for item in value)
        if isinstance(value, tuple):
            return any(PolicyEngine._contains_sensitive_key(item) for item in value)
        return False

    def _allow_or_redact(self, *, args: dict[str, Any], reason: str) -> PolicyDecision:
        if not self._policy.get("auto_redact_args", False):
            return PolicyDecision(ALLOW, reason)

        redactions = self._collect_redactions(args)
        if redactions:
            return PolicyDecision(
                ALLOW_WITH_REDACTION,
                "allowed with argument redactions",
                redactions=redactions,
            )
        return PolicyDecision(ALLOW, reason)

    @staticmethod
    def _collect_redactions(value: Any, prefix: str = "") -> dict[str, str]:
        redactions: dict[str, str] = {}
        if isinstance(value, dict):
            for key, nested in value.items():
                key_str = str(key)
                path = f"{prefix}.{key_str}" if prefix else key_str
                lowered = key_str.lower()
                if any(token in lowered for token in _SENSITIVE_TOKENS):
                    redactions[path] = "***"
                else:
                    redactions.update(PolicyEngine._collect_redactions(nested, path))
        elif isinstance(value, (list, tuple)):
            for item in value:
                redactions.update(PolicyEngine._collect_redactions(item, prefix))
        return redactions

    @staticmethod
    def _path_scope(path_value: Any) -> str:
        if not isinstance(path_value, str) or not path_value:
            return "invalid"

        candidate = path_value.replace("\\", "/")
        posix = PurePosixPath(candidate)
        if posix.is_absolute():
            return "invalid"

        parts = [part for part in posix.parts if part not in ("", ".")]
        if not parts:
            return "invalid"
        if any(part == ".." for part in parts):
            return "invalid"

        root = parts[0]
        if root == "public":
            return "public"
        if root == "private":
            return "private"
        if root == "workspace":
            return "workspace"
        return "other"
