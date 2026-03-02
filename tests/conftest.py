from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pytest


@dataclass(frozen=True)
class CliResult:
    exit_code: int
    stdout: str
    stderr: str


class CliRunner:
    """
    Subprocess CLI runner for argparse-based commands.
    """

    def __init__(self, *, cwd: Path) -> None:
        self._cwd = cwd

    def invoke(self, args: list[str], *, cwd: Path | None = None) -> CliResult:
        env = os.environ.copy()
        env.setdefault("PYTHONHASHSEED", "0")
        repo_root = Path(__file__).resolve().parents[1]
        src_path = repo_root / "src"
        env["PYTHONPATH"] = str(src_path)

        completed = subprocess.run(
            [sys.executable, "-m", "agent_sentinel.cli", *args],
            cwd=cwd or self._cwd,
            env=env,
            text=True,
            capture_output=True,
        )
        return CliResult(
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )


@pytest.fixture
def temp_workdir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def runner(temp_workdir: Path) -> CliRunner:
    return CliRunner(cwd=temp_workdir)


@pytest.fixture
def run_cli(runner: CliRunner) -> Callable[[list[str]], CliResult]:
    def _run(args: list[str]) -> CliResult:
        return runner.invoke(args)

    return _run
