from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_sentinel.capabilities.base import Capability, Result  # noqa: E402
from agent_sentinel.capabilities.plugins import (  # noqa: E402
    discover_entrypoint_capabilities,
    load_capabilities,
)
from agent_sentinel.capabilities.registry import CapabilityRegistry  # noqa: E402
from agent_sentinel.cli import main  # noqa: E402
from agent_sentinel.cli_exit_codes import OK, RUNTIME, ExitCode  # noqa: E402


class _FakeEntryPoint:
    def __init__(self, *, name: str, value: str, loader: Any) -> None:
        self.name = name
        self.value = value
        self.group = "agent_sentinel.capabilities"
        self._loader = loader

    def load(self) -> object:
        if isinstance(self._loader, Exception):
            raise self._loader
        return self._loader


class _FakeEntryPoints(list[_FakeEntryPoint]):
    def select(self, *, group: str) -> list[_FakeEntryPoint]:
        return [entry for entry in self if entry.group == group]


class _PluginCapability(Capability):
    name = "plugin.good"

    def execute(self, payload: dict[str, Any]) -> Result:
        return Result(ok=True, code=ExitCode.OK, data=payload)


def test_discover_entrypoint_capabilities_filters_group(monkeypatch: pytest.MonkeyPatch) -> None:
    entries = _FakeEntryPoints(
        [
            _FakeEntryPoint(name="b", value="b.mod:obj", loader=_PluginCapability),
            _FakeEntryPoint(name="a", value="a.mod:obj", loader=_PluginCapability),
        ]
    )
    monkeypatch.setattr(
        "agent_sentinel.capabilities.plugins.importlib_metadata.entry_points", lambda: entries
    )

    discovered = discover_entrypoint_capabilities()
    assert [entry.name for entry in discovered] == ["a", "b"]


def test_load_capabilities_warns_and_continues(monkeypatch: pytest.MonkeyPatch) -> None:
    local_registry = CapabilityRegistry()
    monkeypatch.setattr("agent_sentinel.capabilities.plugins.registry", local_registry)
    monkeypatch.setattr("agent_sentinel.capabilities.plugins._LOADED_ENTRYPOINTS", set())

    entries = _FakeEntryPoints(
        [
            _FakeEntryPoint(name="good", value="good.mod:obj", loader=_PluginCapability),
            _FakeEntryPoint(name="bad", value="bad.mod:obj", loader=RuntimeError("boom")),
        ]
    )
    monkeypatch.setattr(
        "agent_sentinel.capabilities.plugins.importlib_metadata.entry_points", lambda: entries
    )

    warnings: list[str] = []
    loaded = load_capabilities(strict=False, warn=warnings.append)

    assert loaded == ["good"]
    assert local_registry.get("plugin.good") is _PluginCapability
    assert len(warnings) == 1
    assert "failed to load plugin 'bad'" in warnings[0]


def test_load_capabilities_strict_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    local_registry = CapabilityRegistry()
    monkeypatch.setattr("agent_sentinel.capabilities.plugins.registry", local_registry)
    monkeypatch.setattr("agent_sentinel.capabilities.plugins._LOADED_ENTRYPOINTS", set())

    entries = _FakeEntryPoints(
        [
            _FakeEntryPoint(name="bad", value="bad.mod:obj", loader=RuntimeError("boom")),
        ]
    )
    monkeypatch.setattr(
        "agent_sentinel.capabilities.plugins.importlib_metadata.entry_points", lambda: entries
    )

    with pytest.raises(RuntimeError):
        load_capabilities(strict=True)


def test_load_capabilities_allowlist(monkeypatch: pytest.MonkeyPatch) -> None:
    local_registry = CapabilityRegistry()
    monkeypatch.setattr("agent_sentinel.capabilities.plugins.registry", local_registry)
    monkeypatch.setattr("agent_sentinel.capabilities.plugins._LOADED_ENTRYPOINTS", set())

    class _FirstCapability(Capability):
        name = "plugin.first"

        def execute(self, payload: dict[str, Any]) -> Result:
            return Result(ok=True, code=ExitCode.OK, data=payload)

    class _SecondCapability(Capability):
        name = "plugin.second"

        def execute(self, payload: dict[str, Any]) -> Result:
            return Result(ok=True, code=ExitCode.OK, data=payload)

    entries = _FakeEntryPoints(
        [
            _FakeEntryPoint(name="first", value="first.mod:obj", loader=_FirstCapability),
            _FakeEntryPoint(name="second", value="second.mod:obj", loader=_SecondCapability),
        ]
    )
    monkeypatch.setattr(
        "agent_sentinel.capabilities.plugins.importlib_metadata.entry_points", lambda: entries
    )

    loaded = load_capabilities(allowed=["second"])
    assert loaded == ["second"]
    assert "plugin.second" in local_registry.list()
    assert "plugin.first" not in local_registry.list()


def test_cli_no_plugins_skips_loader(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    called = False

    def _fake_loader(
        *, allowed: list[str] | None = None, strict: bool = False, warn=None
    ) -> list[str]:
        nonlocal called
        _ = (allowed, strict, warn)
        called = True
        return []

    monkeypatch.setattr("agent_sentinel.cli.load_capabilities", _fake_loader)

    rc = main(["--no-plugins", "capabilities", "list"])
    _ = capsys.readouterr()

    assert rc == OK
    assert called is False


def test_cli_plugins_allowlist_file_is_passed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    captured: dict[str, object] = {}

    def _fake_loader(
        *, allowed: list[str] | None = None, strict: bool = False, warn=None
    ) -> list[str]:
        _ = warn
        captured["allowed"] = allowed
        captured["strict"] = strict
        return []

    allowlist = tmp_path / "allowlist.txt"
    allowlist.write_text("alpha\n#comment\nbeta\n", encoding="utf-8")
    monkeypatch.setattr("agent_sentinel.cli.load_capabilities", _fake_loader)

    rc = main(
        [
            "--plugins",
            str(allowlist),
            "--strict-plugins",
            "capabilities",
            "list",
        ]
    )
    _ = capsys.readouterr()

    assert rc == OK
    assert captured["allowed"] == ["alpha", "beta"]
    assert captured["strict"] is True


def test_cli_strict_plugin_failure_returns_runtime(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def _boom(*, allowed: list[str] | None = None, strict: bool = False, warn=None) -> list[str]:
        _ = (allowed, warn)
        if strict:
            raise RuntimeError("plugin failed")
        return []

    monkeypatch.setattr("agent_sentinel.cli.load_capabilities", _boom)

    rc = main(["--strict-plugins", "capabilities", "list"])
    stderr = capsys.readouterr().err

    assert rc == RUNTIME
    assert "plugin failed" in stderr
