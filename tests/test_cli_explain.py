from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


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


def test_cli_explain_includes_reason_code_and_rule_id(tmp_path: Path) -> None:
    policy = {
        "rules": [
            {
                "rule_id": "deny_public_read",
                "action": "deny",
                "capabilities": ["fs.read.public"],
            }
        ]
    }
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(json.dumps(policy), encoding="utf-8")

    result = run_cli(
        [
            "--policy",
            str(policy_path),
            "--capability",
            "fs.read.public",
            "--explain",
        ],
        cwd=tmp_path,
    )

    assert result.returncode != 0
    assert "DENY: capability=fs.read.public" in result.stderr
    assert "rule_id=deny_public_read" in result.stderr
    assert "reason_code=RULE_DENY_MATCH" in result.stderr
    assert "trace:" in result.stderr
