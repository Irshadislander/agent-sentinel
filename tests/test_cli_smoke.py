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


def test_help_returns_exit_code_zero(run_cli) -> None:
    result = run_cli(["--no-plugins", "--help"])
    assert result.exit_code == OK
    assert "usage:" in result.stdout.lower()


def test_capabilities_list_prints_registered_capabilities_in_stable_order(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    local_registry = CapabilityRegistry()

    class _FirstCapability(Capability):
        name = "zeta"

        def execute(self, payload: dict[str, Any]) -> Result:
            return Result(ok=True, code=ExitCode.OK, data=payload)

    class _SecondCapability(Capability):
        name = "alpha"

        def execute(self, payload: dict[str, Any]) -> Result:
            return Result(ok=True, code=ExitCode.OK, data=payload)

    local_registry.register(
        _FirstCapability,
        capability_id="a.capability",
        namespace="demo",
        version="1.0.0",
        description="First",
        tags=["demo"],
        schema={"type": "object"},
    )
    local_registry.register(
        _SecondCapability,
        capability_id="b.capability",
        namespace="demo",
        version="1.0.0",
        description="Second",
        tags=["demo"],
        schema={"type": "object"},
    )

    monkeypatch.setattr("agent_sentinel.cli.registry", local_registry)

    rc = main(["--no-plugins", "capabilities", "list"])
    out_lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]

    assert rc == OK
    assert out_lines[0].startswith("name")
    rows = out_lines[2:]
    parsed_rows = [[part.strip() for part in row.split("|")] for row in rows]
    assert parsed_rows[0][0] == "zeta"
    assert parsed_rows[1][0] == "alpha"


def test_run_command_works_for_example_capability(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    local_registry = CapabilityRegistry()

    class _ExampleCapability(Capability):
        name = "example"

        def execute(self, payload: dict[str, Any]) -> Result:
            return Result(ok=True, code=ExitCode.OK, data={"payload_keys": sorted(payload)})

    local_registry.register(
        _ExampleCapability,
        capability_id="example.capability",
        namespace="demo",
        version="1.0.0",
        description="Example capability",
        tags=["example"],
        schema={"type": "object"},
    )
    monkeypatch.setattr("agent_sentinel.cli.registry", local_registry)

    rc = main(
        [
            "--no-plugins",
            "run",
            "example.capability",
            "--payload",
            "{}",
            "--trace-path",
            str(tmp_path / "trace.jsonl"),
            "--emit-json",
        ]
    )
    out = capsys.readouterr().out.strip()
    payload = json.loads(out)

    assert rc == OK
    assert payload["ok"] is True
    assert payload["capability_id"] == "example.capability"
