from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class AuditEvent:
    timestamp_utc: str
    capability: str
    decision: str  # "allow" | "deny"
    reason: str
    allowed_capabilities: list[str] | None = None


def now_utc_iso() -> str:
    return datetime.now(UTC).isoformat()


def to_json(event: AuditEvent) -> str:
    return json.dumps(asdict(event), sort_keys=True)


def from_exception(exc: Exception, *, capability: str) -> AuditEvent:
    # Keep this generic; we map known errors in policy_engine.
    return AuditEvent(
        timestamp_utc=now_utc_iso(),
        capability=capability,
        decision="deny",
        reason=exc.__class__.__name__,
    )
