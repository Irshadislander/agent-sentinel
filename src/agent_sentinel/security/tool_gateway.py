from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Callable

from agent_sentinel.forensics.ledger import FlightRecorder
from agent_sentinel.security.capabilities import CapabilitySet
from agent_sentinel.security.policy_engine import (
    ALLOW,
    ALLOW_WITH_REDACTION,
    DENY,
    REQUIRE_APPROVAL,
    PolicyEngine,
)

_SENSITIVE_TOKENS = ("key", "token", "secret", "password")


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    )


def _contains_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return any(token in lowered for token in _SENSITIVE_TOKENS)


def _sanitize_for_log(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for raw_key, raw_value in value.items():
            key = str(raw_key)
            if _contains_sensitive_key(key):
                sanitized[key] = "***"
            else:
                sanitized[key] = _sanitize_for_log(raw_value)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_for_log(item) for item in value]
    if isinstance(value, tuple):
        return [_sanitize_for_log(item) for item in value]
    return value


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


def _result_summary(result: dict[str, Any]) -> dict[str, Any]:
    serialized = _canonical_json(result)
    encoded = serialized.encode("utf-8")
    return {
        "output_hash": hashlib.sha256(encoded).hexdigest(),
        "output_bytes": len(encoded),
        "result_keys": sorted(result.keys()),
    }


class ToolGateway:
    def __init__(
        self,
        *,
        policy: dict[str, Any],
        recorder: FlightRecorder,
        caps: CapabilitySet,
        tools: dict[str, Callable[..., Any]],
    ) -> None:
        self._policy_engine = PolicyEngine(policy)
        self._recorder = recorder
        self._caps = caps
        self._tools = dict(tools)

    def execute(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(args, dict):
            raise TypeError("args must be a dictionary")

        safe_args = _sanitize_for_log(args)
        self._recorder.append(
            "tool.call.requested",
            {
                "tool_name": tool_name,
                "args": safe_args,
            },
        )

        decision = self._policy_engine.decide(
            tool_name=tool_name,
            args=args,
            caps=set(self._caps.granted),
        )
        self._recorder.append(
            "policy.decision",
            {
                "tool_name": tool_name,
                "verdict": decision.verdict,
                "reason": decision.reason,
                "redactions": decision.redactions or {},
            },
        )

        if decision.verdict == DENY:
            self._recorder.append(
                "tool.call.blocked",
                {
                    "tool_name": tool_name,
                    "reason": decision.reason,
                },
            )
            raise PermissionError(decision.reason)

        if decision.verdict == REQUIRE_APPROVAL:
            self._recorder.append(
                "tool.call.needs_approval",
                {
                    "tool_name": tool_name,
                    "reason": decision.reason,
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
                    "reason": "unknown tool",
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
                    "error": f"{type(exc).__name__}: {exc}",
                },
            )
            raise

        if not isinstance(result, dict):
            self._recorder.append(
                "tool.call.failed",
                {
                    "tool_name": tool_name,
                    "error": "TypeError: tool result must be a dictionary",
                },
            )
            raise TypeError("tool result must be a dictionary")

        self._recorder.append(
            "tool.call.completed",
            {
                "tool_name": tool_name,
                **_result_summary(result),
            },
        )
        return result
