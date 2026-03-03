from __future__ import annotations

from agent_sentinel.security.capabilities import FS_READ_PUBLIC
from agent_sentinel.security.policy_engine import resolve_decision, verify_trace_commitment


def test_trace_integrity_detects_modified_entry() -> None:
    policy = {"allow": [FS_READ_PUBLIC], "trace_integrity": True}
    result = resolve_decision(FS_READ_PUBLIC, policy)

    assert result.trace_commitment is not None
    assert verify_trace_commitment(result.evaluation_trace, result.trace_commitment)

    tampered_trace = list(result.evaluation_trace)
    tampered_trace[0] = f"{tampered_trace[0]}:tampered"
    assert not verify_trace_commitment(tampered_trace, result.trace_commitment)


def test_trace_integrity_detects_truncated_trace() -> None:
    policy = {"allow": [FS_READ_PUBLIC], "trace_integrity": True}
    result = resolve_decision(FS_READ_PUBLIC, policy)

    assert result.trace_commitment is not None
    truncated_trace = result.evaluation_trace[:-1]
    assert not verify_trace_commitment(truncated_trace, result.trace_commitment)


def test_trace_integrity_optional_mode_can_be_disabled() -> None:
    policy = {"allow": [FS_READ_PUBLIC], "trace_integrity": False}
    result = resolve_decision(FS_READ_PUBLIC, policy)

    assert result.trace_commitment is None
