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
from agent_sentinel.cli_exit_codes import OK, USAGE, ExitCode  # noqa: E402


class _EchoCapability(Capability):
    name = "echo.capability"

    def execute(self, payload: dict[str, Any]) -> Result:
        value = payload.get("value")
        return Result(ok=True, code=ExitCode.OK, data={"echo": value})


def test_cli_run_traces_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    local_registry = CapabilityRegistry()
    local_registry.register(
        _EchoCapability,
        capability_id="demo.echo",
        namespace="demo",
        version="1.0.0",
        description="Echo capability",
        tags=["demo"],
        schema={
            "type": "object",
            "properties": {"value": {"type": "string"}},
            "required": ["value"],
        },
    )
    monkeypatch.setattr("agent_sentinel.cli.registry", local_registry)

    trace_path = tmp_path / "trace.jsonl"
    rc = main(
        [
            "--no-plugins",
            "run",
            "demo.echo",
            "--payload",
            '{"value":"hello"}',
            "--trace-path",
            str(trace_path),
            "--emit-json",
        ]
    )
    out = capsys.readouterr().out.strip()
    payload = json.loads(out)

    assert rc == OK
    assert payload["ok"] is True
    assert payload["capability_id"] == "demo.echo"

    events = trace_path.read_text(encoding="utf-8").splitlines()
    assert len(events) == 1
    event = json.loads(events[0])
    assert event["capability_id"] == "demo.echo"
    assert event["validation_outcome"] == "passed"
    assert event["exit_code"] == OK
    assert event["duration_ms"] >= 0.0
    assert event["error_kind"] is None


def test_cli_run_validation_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    local_registry = CapabilityRegistry()
    local_registry.register(
        _EchoCapability,
        capability_id="demo.echo",
        namespace="demo",
        version="1.0.0",
        description="Echo capability",
        tags=["demo"],
        schema={
            "type": "object",
            "properties": {"value": {"type": "string"}},
            "required": ["value"],
        },
    )
    monkeypatch.setattr("agent_sentinel.cli.registry", local_registry)

    trace_path = tmp_path / "trace.jsonl"
    rc = main(
        [
            "--no-plugins",
            "run",
            "demo.echo",
            "--payload",
            '{"value": 42}',
            "--trace-path",
            str(trace_path),
            "--emit-json",
        ]
    )
    out = capsys.readouterr().out.strip()
    payload = json.loads(out)

    assert rc == USAGE
    assert payload["ok"] is False
    assert payload["error_kind"] == "validation_error"

    event = json.loads(trace_path.read_text(encoding="utf-8").splitlines()[0])
    assert event["validation_outcome"] == "failed"
    assert event["exit_code"] == USAGE
    assert event["error_kind"] == "validation_error"


def test_cli_trace_view_last(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    local_registry = CapabilityRegistry()
    local_registry.register(
        _EchoCapability,
        capability_id="demo.echo",
        namespace="demo",
        version="1.0.0",
        description="Echo capability",
        tags=["demo"],
        schema={
            "type": "object",
            "properties": {"value": {"type": "string"}},
            "required": ["value"],
        },
    )
    monkeypatch.setattr("agent_sentinel.cli.registry", local_registry)
    trace_path = tmp_path / "trace.jsonl"

    rc1 = main(
        [
            "--no-plugins",
            "run",
            "demo.echo",
            "--payload",
            '{"value":"one"}',
            "--trace-path",
            str(trace_path),
        ]
    )
    rc2 = main(
        [
            "--no-plugins",
            "run",
            "demo.echo",
            "--payload",
            '{"value":"two"}',
            "--trace-path",
            str(trace_path),
        ]
    )
    assert rc1 == OK
    assert rc2 == OK

    rc = main(
        [
            "--no-plugins",
            "trace",
            "view",
            "--trace-path",
            str(trace_path),
            "--last",
            "1",
        ]
    )
    out = capsys.readouterr().out

    assert rc == OK
    assert "capability_id" in out
    assert "demo.echo" in out
    assert out.count("demo.echo") == 1


def test_cli_trace_view_emit_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    local_registry = CapabilityRegistry()
    local_registry.register(
        _EchoCapability,
        capability_id="demo.echo",
        namespace="demo",
        version="1.0.0",
        description="Echo capability",
        tags=["demo"],
        schema={
            "type": "object",
            "properties": {"value": {"type": "string"}},
            "required": ["value"],
        },
    )
    monkeypatch.setattr("agent_sentinel.cli.registry", local_registry)
    trace_path = tmp_path / "trace.jsonl"

    rc1 = main(
        [
            "--no-plugins",
            "run",
            "demo.echo",
            "--payload",
            '{"value":"json"}',
            "--trace-path",
            str(trace_path),
        ]
    )
    assert rc1 == OK
    _ = capsys.readouterr()

    rc = main(
        [
            "--no-plugins",
            "trace",
            "view",
            "--trace-path",
            str(trace_path),
            "--last",
            "20",
            "--emit-json",
        ]
    )
    out = capsys.readouterr().out.strip()
    data = json.loads(out)

    assert rc == OK
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[-1]["capability_id"] == "demo.echo"
