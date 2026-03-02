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


class _ValidationCapability(Capability):
    name = "validation.capability"

    def execute(self, payload: dict[str, Any]) -> Result:
        return Result(ok=True, code=ExitCode.OK, data={"payload": payload})


def _register_validation_capability(registry: CapabilityRegistry) -> None:
    registry.register(
        _ValidationCapability,
        capability_id="validation.example",
        namespace="demo",
        version="1.0.0",
        description="Validation example",
        tags=["validation"],
        schema={
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    )


def test_invalid_payload_returns_structured_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    local_registry = CapabilityRegistry()
    _register_validation_capability(local_registry)
    monkeypatch.setattr("agent_sentinel.cli.registry", local_registry)

    rc = main(
        [
            "--no-plugins",
            "run",
            "validation.example",
            "--payload",
            '{"name": 123}',
            "--trace-path",
            str(tmp_path / "trace.jsonl"),
            "--emit-json",
        ]
    )
    payload = json.loads(capsys.readouterr().out.strip())

    assert rc == USAGE
    assert payload["ok"] is False
    assert payload["capability_id"] == "validation.example"
    assert payload["error_kind"] == "validation_error"
    assert payload["exit_code"] == USAGE


def test_payload_omitted_defaults_to_empty_dict(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    local_registry = CapabilityRegistry()

    class _EmptyPayloadCapability(Capability):
        name = "empty.payload.capability"

        def execute(self, payload: dict[str, Any]) -> Result:
            return Result(ok=True, code=ExitCode.OK, data={"payload": payload})

    local_registry.register(
        _EmptyPayloadCapability,
        capability_id="validation.empty",
        namespace="demo",
        version="1.0.0",
        description="Accept empty payload",
        tags=["validation"],
        schema={"type": "object"},
    )
    monkeypatch.setattr("agent_sentinel.cli.registry", local_registry)

    rc = main(
        [
            "--no-plugins",
            "run",
            "validation.empty",
            "--trace-path",
            str(tmp_path / "trace.jsonl"),
            "--emit-json",
        ]
    )
    payload = json.loads(capsys.readouterr().out.strip())

    assert rc == OK
    assert payload["ok"] is True
    assert payload["data"]["payload"] == {}
