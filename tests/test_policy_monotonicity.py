from __future__ import annotations

from agent_sentinel.security.capabilities import (
    ALL_CAPABILITIES,
    FS_READ_PUBLIC,
    FS_WRITE_WORKSPACE,
    NET_HTTP_GET,
)
from agent_sentinel.security.policy_engine import resolve_decision


def _allowed_set(policy: dict[str, object], capabilities: list[str]) -> set[str]:
    return {
        capability
        for capability in capabilities
        if resolve_decision(capability, policy).decision == "allow"
    }


def test_allowed_set_is_monotonic_under_added_deny_rule() -> None:
    capability_universe = sorted(ALL_CAPABILITIES)

    baseline_policy = {
        "rules": [
            {
                "rule_id": "allow_public",
                "action": "allow",
                "capabilities": [FS_READ_PUBLIC],
            },
            {
                "rule_id": "allow_workspace",
                "action": "allow",
                "capabilities": [FS_WRITE_WORKSPACE],
            },
            {
                "rule_id": "allow_http_get",
                "action": "allow",
                "capabilities": [NET_HTTP_GET],
            },
        ]
    }
    strengthened_policy = {
        "rules": [
            {
                "rule_id": "deny_workspace",
                "action": "deny",
                "capabilities": [FS_WRITE_WORKSPACE],
            },
            *baseline_policy["rules"],
        ]
    }

    allowed_baseline = _allowed_set(baseline_policy, capability_universe)
    allowed_strengthened = _allowed_set(strengthened_policy, capability_universe)

    assert allowed_strengthened <= allowed_baseline
    assert FS_WRITE_WORKSPACE in allowed_baseline
    assert FS_WRITE_WORKSPACE not in allowed_strengthened
