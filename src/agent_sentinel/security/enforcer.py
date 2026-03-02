from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .audit import AuditEvent
from .errors import AgentSentinelError
from .policy_engine import enforce_request as enforce_policy_request


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
    audit_sink: Callable[[AuditEvent], None] | None = None,
) -> None:
    """
    Runtime enforcement entrypoint.

    - Raises structured AgentSentinelError subclasses when blocked
    - Returns None when allowed
    """

    _ = context  # reserved for future logging/audit trail
    enforce_policy_request(capability, policy, audit_sink=audit_sink)


def is_request_allowed(
    capability: str,
    policy: Any,
    *,
    context: EnforcementContext | None = None,
    audit_sink: Callable[[AuditEvent], None] | None = None,
) -> bool:
    """
    Convenience bool wrapper for runtime callers.
    """

    try:
        enforce_request(capability, policy, context=context, audit_sink=audit_sink)
        return True
    except AgentSentinelError:
        return False
