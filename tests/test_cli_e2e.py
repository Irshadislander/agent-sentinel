from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from agent_sentinel.security.policy_engine import RULE_ALLOW_MATCH, RULE_DENY_MATCH


def run_cli(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    src_dir = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = str(src_dir)
    return subprocess.run(
        [sys.executable, "-m", "agent_sentinel.cli", *args],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
    )


def _json_lines(text: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _write_policy(path: Path, policy: dict[str, object]) -> None:
    path.write_text(json.dumps(policy), encoding="utf-8")


def test_cli_e2e_allow_case_includes_decision_and_reason_code(tmp_path: Path) -> None:
    policy_path = tmp_path / "allow.json"
    _write_policy(policy_path, {"allow": ["fs.read.public"]})

    result = run_cli(
        [
            "--policy",
            str(policy_path),
            "--capability",
            "fs.read.public",
            "--audit-json",
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 0
    assert "ALLOWED" in result.stdout
    events = _json_lines(result.stderr)
    assert events
    event = events[-1]
    assert {"decision", "reason_code", "rule_id"} <= set(event)
    assert event["decision"] == "allow"
    assert event["reason_code"] == RULE_ALLOW_MATCH


def test_cli_e2e_deny_case_includes_decision_and_reason_code(tmp_path: Path) -> None:
    policy_path = tmp_path / "deny.json"
    _write_policy(
        policy_path,
        {
            "rules": [
                {
                    "rule_id": "deny_public",
                    "action": "deny",
                    "capabilities": ["fs.read.public"],
                }
            ]
        },
    )

    result = run_cli(
        [
            "--policy",
            str(policy_path),
            "--capability",
            "fs.read.public",
            "--audit-json",
            "--json",
            "--explain",
        ],
        cwd=tmp_path,
    )

    assert result.returncode != 0
    events = _json_lines(result.stderr)
    assert events
    audit_event = events[0]
    assert {"decision", "reason_code", "rule_id"} <= set(audit_event)
    assert audit_event["decision"] == "deny"
    assert audit_event["reason_code"] == RULE_DENY_MATCH
    assert audit_event["rule_id"] == "deny_public"
    assert "DENY: capability=fs.read.public" in result.stderr


def test_cli_e2e_missing_policy(tmp_path: Path) -> None:
    result = run_cli(
        [
            "--policy",
            str(tmp_path / "missing.json"),
            "--capability",
            "fs.read.public",
            "--audit-json",
            "--json",
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 2
    events = _json_lines(result.stderr)
    assert events
    audit_event = events[0]
    assert {"decision", "reason_code"} <= set(audit_event)
    assert audit_event["decision"] == "deny"
    payload = events[-1]
    assert payload.get("code") == "policy_file_not_found"


def test_cli_e2e_invalid_policy(tmp_path: Path) -> None:
    policy_path = tmp_path / "invalid.json"
    policy_path.write_text("{ not json", encoding="utf-8")

    result = run_cli(
        [
            "--policy",
            str(policy_path),
            "--capability",
            "fs.read.public",
            "--audit-json",
            "--json",
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 3
    events = _json_lines(result.stderr)
    assert events
    audit_event = events[0]
    assert {"decision", "reason_code"} <= set(audit_event)
    assert audit_event["decision"] == "deny"
    payload = events[-1]
    assert payload.get("code") == "policy_parse_error"
