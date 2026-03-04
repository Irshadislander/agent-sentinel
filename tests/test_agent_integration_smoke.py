from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_agent_integration_case_study_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    out = repo_root / "artifacts" / "agent_integration" / "case_study_results.json"

    # ensure clean output
    if out.exists():
        out.unlink()

    env = dict(**{k: v for k, v in dict(**__import__("os").environ).items()})
    env["PYTHONPATH"] = "src"

    subprocess.check_call(
        [sys.executable, "examples/agent_integration/run_case_study.py"],
        cwd=str(repo_root),
        env=env,
    )

    assert out.exists()
    data = json.loads(out.read_text())
    assert "attack_block_rate" in data
    assert 0.0 <= data["attack_block_rate"] <= 1.0
