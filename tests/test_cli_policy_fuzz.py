from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from agent_sentinel.cli import MAX_NESTING_DEPTH, MAX_POLICY_BYTES


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


def _error_payload(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    for line in reversed(result.stderr.splitlines()):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return {}


def test_policy_loader_rejects_giant_policy_input(tmp_path: Path) -> None:
    oversized = " " * (MAX_POLICY_BYTES + 1)
    policy_path = tmp_path / "oversized.json"
    policy_path.write_text(oversized, encoding="utf-8")

    result = run_cli(
        ["--policy", str(policy_path), "--capability", "fs.read.public", "--json"],
        cwd=tmp_path,
    )

    assert result.returncode == 3
    payload = _error_payload(result)
    assert payload.get("code") == "policy_parse_error"
    details = payload.get("details", {})
    assert isinstance(details, dict)
    assert "MAX_POLICY_BYTES" in str(details.get("reason", ""))


def test_policy_loader_rejects_deeply_nested_policy(tmp_path: Path) -> None:
    nested: list[object] = ["fs.read.public"]
    for _ in range(MAX_NESTING_DEPTH + 2):
        nested = [nested]

    policy = {
        "rules": [
            {
                "rule_id": "allow_public",
                "action": "allow",
                "capabilities": nested,
            }
        ]
    }
    policy_path = tmp_path / "deep.json"
    policy_path.write_text(json.dumps(policy), encoding="utf-8")

    result = run_cli(
        ["--policy", str(policy_path), "--capability", "fs.read.public", "--json"],
        cwd=tmp_path,
    )

    assert result.returncode == 3
    payload = _error_payload(result)
    assert payload.get("code") == "policy_parse_error"
    details = payload.get("details", {})
    assert isinstance(details, dict)
    assert "MAX_NESTING_DEPTH" in str(details.get("reason", ""))


def test_policy_loader_handles_weird_types_and_unicode_keys(tmp_path: Path) -> None:
    policy = {
        "allow": {"not": "a-list"},
        "🚫": "unexpected",
    }
    policy_path = tmp_path / "weird.json"
    policy_path.write_text(json.dumps(policy), encoding="utf-8")

    result = run_cli(
        ["--policy", str(policy_path), "--capability", "fs.read.public", "--json"],
        cwd=tmp_path,
    )

    assert result.returncode == 3
    payload = _error_payload(result)
    assert payload.get("code") == "policy_parse_error"
