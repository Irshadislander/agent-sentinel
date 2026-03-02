from __future__ import annotations

from collections.abc import Iterable


class AgentSentinelError(Exception):
    """Base exception for Agent Sentinel."""


class InvalidPolicyFormatError(AgentSentinelError):
    """Raised when the policy object is malformed."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid policy format: {reason}")


class UnknownCapabilityError(AgentSentinelError):
    """Raised when a capability is not recognized by the system."""

    def __init__(self, requested_capability: str) -> None:
        self.requested_capability = requested_capability
        super().__init__(
            f"Unknown capability: '{requested_capability}'. This capability is not registered."
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
            "Policy violation: "
            f"'{self.requested_capability}' denied. "
            f"Allowed capabilities: {self.allowed_capabilities}. "
            f"Reason: {self.reason}"
        )
