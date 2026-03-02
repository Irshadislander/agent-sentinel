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


def test_missing_policy_file_returns_exit_2(tmp_path: Path) -> None:
    result = run_cli(["--policy", "nope.json", "--capability", "fs.read.public"], cwd=tmp_path)
    assert result.returncode == 2
    assert "Policy file not found" in result.stderr


def test_missing_policy_file_json_output(tmp_path: Path) -> None:
    result = run_cli(
        ["--policy", "nope.json", "--capability", "fs.read.public", "--json"],
        cwd=tmp_path,
    )
    assert result.returncode == 2
    payload = json.loads(result.stderr.strip())
    assert payload["code"] == "policy_file_not_found"
    assert payload["details"]["path"].endswith("nope.json")


def test_invalid_json_policy_returns_exit_3(tmp_path: Path) -> None:
    (tmp_path / "bad.json").write_text("{not json", encoding="utf-8")
    result = run_cli(["--policy", "bad.json", "--capability", "fs.read.public"], cwd=tmp_path)
    assert result.returncode == 3
    assert "Failed to parse policy file" in result.stderr
