from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ErrorPayload:
    code: str
    message: str
    details: dict[str, Any] | None = None
    hint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.details:
            out["details"] = self.details
        if self.hint:
            out["hint"] = self.hint
        return out


class AgentSentinelError(Exception):
    """
    Base class for all user-facing errors in Agent Sentinel.

    These errors are safe to show to end users.
    """

    exit_code: int = 1  # default: generic failure

    def __init__(
        self,
        message: str,
        *,
        code: str = "agent_sentinel_error",
        details: dict[str, Any] | None = None,
        hint: str | None = None,
    ) -> None:
        super().__init__(message)
        self.payload = ErrorPayload(code=code, message=message, details=details, hint=hint)

    def to_payload(self) -> ErrorPayload:
        return self.payload


class PolicyFileNotFoundError(AgentSentinelError):
    exit_code = 2

    def __init__(self, path: str) -> None:
        super().__init__(
            f"Policy file not found: {path}",
            code="policy_file_not_found",
            details={"path": path},
            hint="Pass a valid --policy path (e.g., ./policy.json).",
        )


class PolicyParseError(AgentSentinelError):
    exit_code = 3

    def __init__(self, path: str, reason: str) -> None:
        super().__init__(
            f"Failed to parse policy file: {path}",
            code="policy_parse_error",
            details={"path": path, "reason": reason},
            hint="Ensure the policy file is valid JSON.",
        )


class UnknownCapabilityError(AgentSentinelError):
    exit_code = 4

    def __init__(self, capability: str) -> None:
        super().__init__(
            f"Unknown capability: {capability}",
            code="unknown_capability",
            details={"capability": capability},
            hint="Check spelling or run `agent-sentinel capabilities` (coming soon).",
        )


class PolicyViolationError(AgentSentinelError):
    exit_code = 5

    def __init__(self, capability: str, *, reason: str | None = None) -> None:
        details: dict[str, Any] = {"capability": capability}
        if reason:
            details["reason"] = reason
        super().__init__(
            f"Capability denied: {capability}",
            code="policy_violation",
            details=details,
            hint="Update the policy allowlist or request a permitted capability.",
        )
