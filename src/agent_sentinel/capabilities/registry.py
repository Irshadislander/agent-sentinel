from __future__ import annotations

from .base import Capability, CapabilityError


class CapabilityRegistry:
    """
    Central registry for all agent capabilities.
    """

    def __init__(self) -> None:
        self._registry: dict[str, type[Capability]] = {}

    def register(self, capability_cls: type[Capability]) -> None:
        name = getattr(capability_cls, "name", None)

        if not name:
            raise CapabilityError("Capability must define a 'name' attribute.")

        if name in self._registry:
            raise CapabilityError(f"Capability '{name}' already registered.")

        self._registry[name] = capability_cls

    def get(self, name: str) -> type[Capability]:
        if name not in self._registry:
            raise CapabilityError(f"Capability '{name}' is not registered.")

        return self._registry[name]

    def list(self) -> dict[str, type[Capability]]:
        return dict(self._registry)
