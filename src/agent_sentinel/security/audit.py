from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime

from .context import RequestContext


@dataclass(frozen=True)
class AuditEvent:
    timestamp_utc: str
    request_id: str
    correlation_id: str | None
    source: str
    capability: str
    decision: str  # "allow" | "deny"
    reason: str
    allowed_capabilities: list[str] | None = None


def now_utc_iso() -> str:
    return datetime.now(UTC).isoformat()


def to_json(event: AuditEvent) -> str:
    return json.dumps(asdict(event), sort_keys=True)


def make_event(
    *,
    ctx: RequestContext,
    capability: str,
    decision: str,
    reason: str,
    allowed_capabilities: list[str] | None = None,
) -> AuditEvent:
    return AuditEvent(
        timestamp_utc=now_utc_iso(),
        request_id=ctx.request_id,
        correlation_id=ctx.correlation_id,
        source=ctx.source,
        capability=capability,
        decision=decision,
        reason=reason,
        allowed_capabilities=allowed_capabilities,
    )


def from_exception(exc: Exception, *, ctx: RequestContext, capability: str) -> AuditEvent:
    # Keep this generic; we map known errors in policy_engine.
    return make_event(
        ctx=ctx,
        capability=capability,
        decision="deny",
        reason=exc.__class__.__name__,
    )
