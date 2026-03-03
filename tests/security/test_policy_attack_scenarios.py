from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from agent_sentinel.security.capabilities import FS_READ_PUBLIC
from agent_sentinel.security.policy_engine import (
    DEFAULT_DENY_NO_MATCH,
    DENY,
    RULE_DENY_MATCH,
    PolicyEngine,
    resolve_decision,
)


def test_policy_bypass_attempt_denied_with_trace_signature() -> None:
    bypass_capability = "fs.read.private"
    policy = {"allow": [FS_READ_PUBLIC]}

    result = resolve_decision(bypass_capability, policy)

    assert result.decision == "deny"
    assert result.reason_code in {DEFAULT_DENY_NO_MATCH, RULE_DENY_MATCH}
    assert "no_match" in result.evaluation_trace or any(
        item.startswith("match:") and item.endswith(":deny") for item in result.evaluation_trace
    )


def test_plugin_override_attempt_tool_alias_spoofing_is_denied() -> None:
    engine = PolicyEngine(policy={})
    spoofed_aliases = [
        "TOOLS.HTTP.GET",
        " http_get ",
        "Fs_Tool.Read_Text",
        "WRITE_TEXT",
    ]

    for tool_name in spoofed_aliases:
        decision = engine.decide(
            tool_name=tool_name,
            args={"url": "https://example.com", "path": "public/readme.md", "text": "x"},
            caps=set(),
        )
        assert decision.verdict == DENY


def test_trace_suppression_attempt_weird_context_keeps_trace_and_determinism() -> None:
    capability = FS_READ_PUBLIC
    weird_policy = {"allow": [FS_READ_PUBLIC]}
    weird_context = {"trace": None, "evaluation_trace": ["pretend"], "suppress": True}

    first = resolve_decision(capability, weird_policy, context=weird_context)
    second = resolve_decision(capability, weird_policy, context=weird_context)

    assert first.decision == second.decision
    assert first.reason_code == second.reason_code
    assert first.rule_id == second.rule_id
    assert first.evaluation_trace == second.evaluation_trace
    assert first.evaluation_trace
