from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_sentinel.capabilities import register_capability  # noqa: E402
from agent_sentinel.capabilities import registry as global_registry  # noqa: E402
from agent_sentinel.capabilities.base import Capability  # noqa: E402
from agent_sentinel.capabilities.registry import CapabilityRegistry  # noqa: E402
from agent_sentinel.cli import main  # noqa: E402
from agent_sentinel.cli_exit_codes import OK  # noqa: E402


class _DuplicateCapability(Capability):
    name = "test.duplicate"

    def execute(self, payload: dict[str, object]) -> dict[str, object]:
        return payload


def test_duplicate_registration_fails() -> None:
    local_registry = CapabilityRegistry()
    local_registry.register(_DuplicateCapability)

    with pytest.raises(ValueError):
        local_registry.register(_DuplicateCapability)


def test_decorator_registers_correct_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    local_registry = CapabilityRegistry()
    monkeypatch.setattr("agent_sentinel.capabilities.registry", local_registry)

    @register_capability(
        name="demo.capability",
        namespace="agent_sentinel.demo",
        version="1.2.3",
        description="Demo capability for registry testing",
        tags=["demo", "test"],
    )
    class _DecoratedCapability(Capability):
        name = "ignored.by.metadata"

        def execute(self, payload: dict[str, object]) -> dict[str, object]:
            return payload

    registered = local_registry.get("demo.capability")
    metadata = local_registry.get_metadata("demo.capability")

    assert registered is _DecoratedCapability
    assert metadata.name == "demo.capability"
    assert metadata.namespace == "agent_sentinel.demo"
    assert metadata.version == "1.2.3"
    assert metadata.description == "Demo capability for registry testing"
    assert metadata.tags == ["demo", "test"]


def test_cli_capabilities_list_prints_entries(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    local_registry = CapabilityRegistry()

    class _ListCapability(Capability):
        name = "tools.echo"

        def execute(self, payload: dict[str, object]) -> dict[str, object]:
            return payload

    local_registry.register(
        _ListCapability,
        namespace="agent_sentinel.tools",
        version="0.1.0",
        description="Echo payload",
        tags=["utility"],
    )

    monkeypatch.setattr("agent_sentinel.cli.registry", local_registry)

    rc = main(["capabilities", "list"])
    out = capsys.readouterr().out

    assert rc == OK
    assert "name" in out
    assert "namespace" in out
    assert "version" in out
    assert "description" in out
    assert "tools.echo" in out
    assert "agent_sentinel.tools" in out
    assert "0.1.0" in out
    assert "Echo payload" in out


@pytest.fixture(autouse=True)
def _restore_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("agent_sentinel.capabilities.registry", global_registry)
