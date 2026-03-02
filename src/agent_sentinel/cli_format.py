from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from agent_sentinel.security.errors import (
    AgentSentinelError,
    InvalidPolicyFormatError,
    PolicyViolationError,
    UnknownCapabilityError,
)


@dataclass(frozen=True)
class ErrorPayload:
    error_type: str
    message: str
    requested_capability: str | None = None
    allowed_capabilities: list[str] | None = None
    reason: str | None = None


def to_payload(err: AgentSentinelError) -> ErrorPayload:
    if isinstance(err, PolicyViolationError):
        return ErrorPayload(
            error_type=err.__class__.__name__,
            message=str(err),
            requested_capability=err.requested_capability,
            allowed_capabilities=err.allowed_capabilities,
            reason=err.reason,
        )

    if isinstance(err, UnknownCapabilityError):
        return ErrorPayload(
            error_type=err.__class__.__name__,
            message=str(err),
            requested_capability=err.requested_capability,
        )

    if isinstance(err, InvalidPolicyFormatError):
        return ErrorPayload(
            error_type=err.__class__.__name__,
            message=str(err),
            reason=err.reason,
        )

    return ErrorPayload(error_type=err.__class__.__name__, message=str(err))


def render(err: AgentSentinelError, *, as_json: bool) -> str:
    payload = to_payload(err)
    if as_json:
        return json.dumps(asdict(payload), indent=2, sort_keys=True)

    # Human-readable format
    lines: list[str] = [f"{payload.error_type}: {payload.message}"]

    if payload.requested_capability:
        lines.append(f"requested_capability: {payload.requested_capability}")
    if payload.reason:
        lines.append(f"reason: {payload.reason}")
    if payload.allowed_capabilities is not None:
        lines.append("allowed_capabilities:")
        for cap in payload.allowed_capabilities:
            lines.append(f"  - {cap}")

    return "\n".join(lines)
