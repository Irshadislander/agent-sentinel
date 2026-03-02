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


def write_policy(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def test_missing_version(tmp_path: Path) -> None:
    policy = {"default": "deny", "allow": []}
    write_policy(tmp_path / "p.json", policy)

    result = run_cli(["--policy", "p.json", "--capability", "x"], tmp_path)
    assert result.returncode == 3
    assert "Missing required field: version" in result.stderr


def test_invalid_default(tmp_path: Path) -> None:
    policy = {"version": 1, "default": "invalid", "allow": []}
    write_policy(tmp_path / "p.json", policy)

    result = run_cli(["--policy", "p.json", "--capability", "x"], tmp_path)
    assert result.returncode == 3
    assert "must be 'deny' or 'allow'" in result.stderr


def test_unknown_key(tmp_path: Path) -> None:
    policy = {"version": 1, "default": "deny", "allow": [], "extra": 123}
    write_policy(tmp_path / "p.json", policy)

    result = run_cli(["--policy", "p.json", "--capability", "x"], tmp_path)
    assert result.returncode == 3
    assert "Unknown top-level keys" in result.stderr
