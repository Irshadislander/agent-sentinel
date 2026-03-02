from __future__ import annotations

from collections.abc import Iterable

from agent_sentinel.errors import AgentSentinelError as CoreAgentSentinelError


class AgentSentinelError(CoreAgentSentinelError):
    """Base exception for Agent Sentinel."""


class InvalidPolicyFormatError(AgentSentinelError):
    """Raised when the policy object is malformed."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(
            f"Invalid policy format: {reason}",
            code="invalid_policy_format",
            details={"reason": reason},
            hint="Policy must be a JSON object with `allow` as a list of capability strings.",
        )


class UnknownCapabilityError(AgentSentinelError):
    """Raised when a capability is not recognized by the system."""

    def __init__(self, requested_capability: str) -> None:
        self.requested_capability = requested_capability
        super().__init__(
            f"Unknown capability: {requested_capability}",
            code="unknown_capability",
            details={"capability": requested_capability},
            hint="Check the capability string against the registered capability list.",
        )


class PolicyViolationError(AgentSentinelError):
    """Raised when a request is denied by policy."""

    def __init__(
        self,
        requested_capability: str,
        allowed_capabilities: Iterable[str],
        reason: str | None = None,
    ) -> None:
        self.requested_capability = requested_capability
        self.allowed_capabilities = list(allowed_capabilities)
        self.reason = reason or "Capability not permitted by policy."

        super().__init__(
            f"Capability denied: {self.requested_capability}",
            code="policy_violation",
            details={
                "capability": self.requested_capability,
                "reason": self.reason,
                "allowed_capabilities": self.allowed_capabilities,
            },
            hint="Update the allowlist or request a permitted capability.",
        )
