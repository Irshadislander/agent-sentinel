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
    rule_id: str | None = None
    reason_code: str = ""
    duration_ms: float = 0.0
    trace_len: int | None = None
    trace_commitment: str | None = None
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
    rule_id: str | None = None,
    reason_code: str = "",
    duration_ms: float = 0.0,
    trace_len: int | None = None,
    trace_commitment: str | None = None,
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
        rule_id=rule_id,
        reason_code=reason_code,
        duration_ms=duration_ms,
        trace_len=trace_len,
        trace_commitment=trace_commitment,
        allowed_capabilities=allowed_capabilities,
    )


def from_exception(exc: Exception, *, ctx: RequestContext, capability: str) -> AuditEvent:
    # Keep this generic; we map known errors in policy_engine.
    return make_event(
        ctx=ctx,
        capability=capability,
        decision="deny",
        reason=exc.__class__.__name__,
        reason_code=exc.__class__.__name__,
    )
