from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_benchmark_module_help_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env.setdefault("PYTHONHASHSEED", "0")
    src_path = repo_root / "src"
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        str(src_path) if not existing_pythonpath else f"{src_path}:{existing_pythonpath}"
    )

    result = subprocess.run(
        [sys.executable, "-m", "agent_sentinel.benchmark.run_benchmark", "--help"],
        cwd=repo_root,
        env=env,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "usage" in result.stdout.lower()
