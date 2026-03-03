import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_sentinel.security.capabilities import FS_READ_PUBLIC
from agent_sentinel.security.policy_engine import (
    DEFAULT_DENY_NO_MATCH,
    POLICY_INVALID,
    POLICY_MISSING,
    RULE_ALLOW_MATCH,
    RULE_DENY_MATCH,
    resolve_decision,
    verify_trace_commitment,
)


def test_resolve_decision_is_deterministic_for_same_input() -> None:
    policy = {"allow": [FS_READ_PUBLIC], "trace_integrity": True}

    first = resolve_decision(FS_READ_PUBLIC, policy)
    second = resolve_decision(FS_READ_PUBLIC, policy)

    assert first.decision == second.decision
    assert first.rule_id == second.rule_id
    assert first.reason_code == second.reason_code
    assert first.evaluation_trace == second.evaluation_trace
    assert first.trace_commitment == second.trace_commitment
    assert first.reason_code == RULE_ALLOW_MATCH
    assert first.trace_commitment is not None
    assert verify_trace_commitment(first.evaluation_trace, first.trace_commitment)
    assert first.duration_ms >= 0.0
    assert second.duration_ms >= 0.0


def test_resolve_decision_default_deny_when_no_match() -> None:
    policy = {"allow": []}

    result = resolve_decision(FS_READ_PUBLIC, policy)

    assert result.decision == "deny"
    assert result.rule_id is None
    assert result.reason_code == DEFAULT_DENY_NO_MATCH
    assert result.evaluation_trace[-1] == f"final:deny:{DEFAULT_DENY_NO_MATCH}"


def test_resolve_decision_policy_missing_and_invalid_reason_codes() -> None:
    missing = resolve_decision(FS_READ_PUBLIC, None)
    invalid = resolve_decision(FS_READ_PUBLIC, {})

    assert missing.decision == "deny"
    assert missing.reason_code == POLICY_MISSING
    assert invalid.decision == "deny"
    assert invalid.reason_code == POLICY_INVALID


def test_resolve_decision_first_match_precedence() -> None:
    policy = {
        "rules": [
            {"rule_id": "deny_first", "action": "deny", "capabilities": [FS_READ_PUBLIC]},
            {"rule_id": "allow_second", "action": "allow", "capabilities": [FS_READ_PUBLIC]},
        ]
    }

    result = resolve_decision(FS_READ_PUBLIC, policy)

    assert result.decision == "deny"
    assert result.rule_id == "deny_first"
    assert result.reason_code == RULE_DENY_MATCH
    assert "eval:deny_first" in result.evaluation_trace
    assert "match:deny_first:deny" in result.evaluation_trace
