from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_sentinel.capabilities.base import Capability, Result  # noqa: E402
from agent_sentinel.capabilities.registry import CapabilityRegistry  # noqa: E402
from agent_sentinel.cli_exit_codes import ExitCode  # noqa: E402


class _RegistryCapability(Capability):
    name = "registry.capability"

    def execute(self, payload: dict[str, Any]) -> Result:
        return Result(ok=True, code=ExitCode.OK, data=payload)


def test_duplicate_capability_id_raises_clear_exception() -> None:
    registry = CapabilityRegistry()
    registry.register(
        _RegistryCapability,
        capability_id="dup.id",
        namespace="demo",
        version="1.0.0",
        description="duplicate id test",
        tags=["test"],
        schema={"type": "object"},
    )

    with pytest.raises(ValueError, match="already registered"):
        registry.register(
            _RegistryCapability,
            capability_id="dup.id",
            name="other-name",
            namespace="demo",
            version="1.0.0",
            description="duplicate id test",
            tags=["test"],
            schema={"type": "object"},
        )


@pytest.mark.parametrize("invalid_id", ["", "   ", "contains space", 123])
def test_invalid_ids_rejected(invalid_id: object) -> None:
    registry = CapabilityRegistry()
    with pytest.raises(ValueError, match="capability id"):
        registry.register(
            _RegistryCapability,
            capability_id=invalid_id,  # type: ignore[arg-type]
            namespace="demo",
            version="1.0.0",
            description="invalid id test",
            tags=["test"],
            schema={"type": "object"},
        )


def test_metadata_required() -> None:
    registry = CapabilityRegistry()
    with pytest.raises(ValueError, match="namespace is required"):
        registry.register(
            _RegistryCapability,
            capability_id="meta.namespace",
            namespace="   ",
            version="1.0.0",
            description="metadata required",
            tags=["test"],
            schema={"type": "object"},
        )

    with pytest.raises(ValueError, match="description is required"):
        registry.register(
            _RegistryCapability,
            capability_id="meta.description",
            namespace="demo",
            version="1.0.0",
            description="   ",
            tags=["test"],
            schema={"type": "object"},
        )


def test_registry_listing_is_deterministic_sorted_by_id() -> None:
    registry = CapabilityRegistry()

    class _AlphaCapability(Capability):
        name = "alpha"

        def execute(self, payload: dict[str, Any]) -> Result:
            return Result(ok=True, code=ExitCode.OK, data=payload)

    class _BetaCapability(Capability):
        name = "beta"

        def execute(self, payload: dict[str, Any]) -> Result:
            return Result(ok=True, code=ExitCode.OK, data=payload)

    registry.register(
        _BetaCapability,
        capability_id="z.id",
        namespace="demo",
        version="1.0.0",
        description="beta",
        tags=["test"],
        schema={"type": "object"},
    )
    registry.register(
        _AlphaCapability,
        capability_id="a.id",
        namespace="demo",
        version="1.0.0",
        description="alpha",
        tags=["test"],
        schema={"type": "object"},
    )

    ordered_ids = [entry.spec.id for entry in registry.entries()]
    assert ordered_ids == ["a.id", "z.id"]
