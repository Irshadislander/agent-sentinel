from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .errors import AgentSentinelError
from .policy_engine import enforce


@dataclass(frozen=True)
class EnforcementContext:
    """
    Optional metadata about the runtime request.

    Keep minimal for now; expand later for audit logs (Day 18/19).
    """

    actor: str | None = None
    tool: str | None = None
    resource: str | None = None


def enforce_request(
    capability: str,
    policy: Any,
    *,
    context: EnforcementContext | None = None,
) -> None:
    """
    Runtime enforcement entrypoint.

    - Raises structured AgentSentinelError subclasses when blocked
    - Returns None when allowed
    """

    _ = context  # reserved for future logging/audit trail
    enforce(capability, policy)


def is_request_allowed(
    capability: str,
    policy: Any,
    *,
    context: EnforcementContext | None = None,
) -> bool:
    """
    Convenience bool wrapper for runtime callers.
    """

    try:
        enforce_request(capability, policy, context=context)
        return True
    except AgentSentinelError:
        return False
