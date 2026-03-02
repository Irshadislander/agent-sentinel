from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from agent_sentinel.forensics.ledger import FlightRecorder
from agent_sentinel.security import validators
from agent_sentinel.security.capabilities import (
    FS_READ_PRIVATE,
    NET_HTTP_GET,
    NET_HTTP_POST,
    CapabilitySet,
)
from agent_sentinel.security.policy_engine import (
    ALLOW,
    ALLOW_WITH_REDACTION,
    DENY,
    REQUIRE_APPROVAL,
    PolicyEngine,
)

_FS_READ_TOOL_NAMES = {"read_text", "fs.read", "fs_read", "fs_tool.read_text"}
_HTTP_REQUEST_TOOL_NAMES = {"http_request", "http.request", "tools.http.request"}
ToolFn = Callable[..., Any]


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    )


def _hash_payload(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _apply_redactions(args: dict[str, Any], redactions: dict[str, Any]) -> dict[str, Any]:
    redacted_args = copy.deepcopy(args)
    for key_path, replacement in redactions.items():
        if not key_path:
            continue
        current: Any = redacted_args
        parts = str(key_path).split(".")
        for part in parts[:-1]:
            if not isinstance(current, dict) or part not in current:
                current = None
                break
            current = current[part]
        if isinstance(current, dict):
            current[parts[-1]] = replacement
    return redacted_args


class ToolGateway:
    def __init__(
        self,
        *,
        policy: dict[str, Any],
        recorder: FlightRecorder,
        caps: CapabilitySet,
        tools: dict[str, ToolFn],
        enable_validation: bool = True,
    ) -> None:
        self._policy = dict(policy)
        self._policy_engine = PolicyEngine(policy)
        self._recorder = recorder
        self._caps = caps
        self._tools: dict[str, ToolFn] = dict(tools)
        self._enable_validation = enable_validation

    def execute(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(args, dict):
            raise TypeError("args must be a dictionary")

        safe_args = validators.redact_secrets(args)
        args_hash = _hash_payload(safe_args)
        self._recorder.append(
            "tool.call.requested",
            {
                "tool_name": tool_name,
                "decision": "REQUESTED",
                "reason": "",
                "args_hash": args_hash,
                "output_hash": "",
                "args": safe_args,
            },
        )

        if self._enable_validation:
            validator_decision = self._validate_tool_call(tool_name=tool_name, args=args)
            if not validator_decision.allowed:
                return self._deny_with_result(
                    tool_name=tool_name,
                    reason=validator_decision.reason,
                    args_hash=args_hash,
                    redacted_args=validator_decision.redacted_args,
                )

        normalized_tool = tool_name.strip().lower()
        if normalized_tool in _HTTP_REQUEST_TOOL_NAMES:
            decision = type(
                "InlineDecision", (), {"verdict": ALLOW, "reason": "ok", "redactions": None}
            )()
        else:
            decision = self._policy_engine.decide(
                tool_name=tool_name,
                args=args,
                caps=set(self._caps.granted),
            )
        self._recorder.append(
            "policy.decision",
            {
                "tool_name": tool_name,
                "decision": decision.verdict,
                "reason": decision.reason,
                "args_hash": args_hash,
                "output_hash": "",
            },
        )

        if decision.verdict == DENY:
            self._recorder.append(
                "tool.call.blocked",
                {
                    "tool_name": tool_name,
                    "decision": DENY,
                    "reason": decision.reason,
                    "args_hash": args_hash,
                    "output_hash": "",
                },
            )
            raise PermissionError(decision.reason)

        if decision.verdict == REQUIRE_APPROVAL:
            self._recorder.append(
                "tool.call.needs_approval",
                {
                    "tool_name": tool_name,
                    "decision": REQUIRE_APPROVAL,
                    "reason": decision.reason,
                    "args_hash": args_hash,
                    "output_hash": "",
                },
            )
            raise PermissionError(f"approval required: {decision.reason}")

        effective_args = args
        if decision.verdict == ALLOW_WITH_REDACTION:
            effective_args = _apply_redactions(args, decision.redactions or {})
            self._recorder.append(
                "tool.call.redacted",
                {
                    "tool_name": tool_name,
                    "decision": ALLOW_WITH_REDACTION,
                    "reason": "args redacted by policy",
                    "args_hash": args_hash,
                    "output_hash": "",
                    "redacted_fields": sorted((decision.redactions or {}).keys()),
                },
            )
        elif decision.verdict != ALLOW:
            raise PermissionError(f"unsupported policy verdict: {decision.verdict}")

        tool = self._tools.get(tool_name)
        if tool is None:
            self._recorder.append(
                "tool.call.blocked",
                {
                    "tool_name": tool_name,
                    "decision": DENY,
                    "reason": "unknown tool",
                    "args_hash": args_hash,
                    "output_hash": "",
                },
            )
            raise PermissionError(f"unknown tool: {tool_name}")

        try:
            result = tool(**effective_args)
        except Exception as exc:
            self._recorder.append(
                "tool.call.failed",
                {
                    "tool_name": tool_name,
                    "decision": "FAILED",
                    "reason": f"{type(exc).__name__}: {exc}",
                    "args_hash": args_hash,
                    "output_hash": "",
                },
            )
            raise

        if not isinstance(result, dict):
            self._recorder.append(
                "tool.call.failed",
                {
                    "tool_name": tool_name,
                    "decision": "FAILED",
                    "reason": "TypeError: tool result must be a dictionary",
                    "args_hash": args_hash,
                    "output_hash": "",
                },
            )
            raise TypeError("tool result must be a dictionary")

        redacted_result = validators.redact_secrets(result)
        output_hash = _hash_payload(redacted_result)
        self._recorder.append(
            "tool.call.completed",
            {
                "tool_name": tool_name,
                "decision": ALLOW,
                "reason": "ok",
                "args_hash": args_hash,
                "output_hash": output_hash,
            },
        )
        return result

    def _deny_with_result(
        self,
        *,
        tool_name: str,
        reason: str,
        args_hash: str,
        redacted_args: dict | None,
    ) -> dict[str, Any]:
        self._recorder.append(
            "policy.decision",
            {
                "tool_name": tool_name,
                "decision": DENY,
                "reason": reason,
                "args_hash": args_hash,
                "output_hash": "",
            },
        )
        self._recorder.append(
            "tool.call.blocked",
            {
                "tool_name": tool_name,
                "decision": DENY,
                "reason": reason,
                "args_hash": args_hash,
                "output_hash": "",
            },
        )
        return {
            "ok": False,
            "tool_name": tool_name,
            "decision": DENY,
            "reason": reason,
            "redacted_args": redacted_args,
        }

    def _validate_tool_call(
        self, *, tool_name: str, args: dict[str, Any]
    ) -> validators.ValidationResult:
        normalized = tool_name.strip().lower()
        base_dir = Path(self._policy.get("base_dir", "."))
        capabilities_map = self._policy.get("capabilities", {})

        if normalized in _FS_READ_TOOL_NAMES:
            allow_private = self._caps.has(FS_READ_PRIVATE) or bool(
                isinstance(capabilities_map, dict) and capabilities_map.get(FS_READ_PRIVATE)
            )
            path = str(args.get("path", ""))
            return validators.validate_fs_read(path, base_dir=base_dir, allow_private=allow_private)

        if normalized in _HTTP_REQUEST_TOOL_NAMES:
            method = str(args.get("method", "GET")).upper()
            url = str(args.get("url", ""))
            if method == "GET" and not self._caps.has(NET_HTTP_GET):
                return validators.ValidationResult(
                    False, f"GET denied: missing capability {NET_HTTP_GET}"
                )
            allowlist = self._policy.get("allowlist_domains", [])
            if not isinstance(allowlist, list):
                allowlist = []
            allow_post = self._caps.has(NET_HTTP_POST)
            return validators.validate_http_request(
                method=method,
                url=url,
                allowlist_domains=[str(item) for item in allowlist],
                allow_post=allow_post,
            )

        return validators.ValidationResult(True, "ok")
