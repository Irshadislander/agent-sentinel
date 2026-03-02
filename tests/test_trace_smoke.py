from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_sentinel.capabilities.base import Capability, Result  # noqa: E402
from agent_sentinel.capabilities.registry import CapabilityRegistry  # noqa: E402
from agent_sentinel.cli import main  # noqa: E402
from agent_sentinel.cli_exit_codes import OK, ExitCode  # noqa: E402


def test_run_writes_trace_event_with_expected_fields(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    local_registry = CapabilityRegistry()

    class _TraceCapability(Capability):
        name = "trace.capability"

        def execute(self, payload: dict[str, Any]) -> Result:
            return Result(ok=True, code=ExitCode.OK, data={"seen": payload})

    local_registry.register(
        _TraceCapability,
        capability_id="trace.example",
        namespace="demo",
        version="1.0.0",
        description="Trace example",
        tags=["trace"],
        schema={"type": "object"},
    )
    monkeypatch.setattr("agent_sentinel.cli.registry", local_registry)

    trace_path = tmp_path / "trace.jsonl"
    rc = main(
        [
            "--no-plugins",
            "run",
            "trace.example",
            "--payload",
            '{"x": 1}',
            "--run-id",
            "run-123",
            "--correlation-id",
            "corr-abc",
            "--trace-path",
            str(trace_path),
        ]
    )
    _ = capsys.readouterr()

    assert rc == OK
    lines = trace_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    event = json.loads(lines[0])
    assert event["capability_id"] == "trace.example"
    assert event["exit_code"] == OK
    assert "duration_ms" in event
    assert float(event["duration_ms"]) >= 0.0
    assert event["run_context"]["run_id"] == "run-123"
    assert event["run_context"]["correlation_id"] == "corr-abc"
    assert "timestamp" in event["run_context"]
