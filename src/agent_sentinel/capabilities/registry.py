from __future__ import annotations

from dataclasses import dataclass

from .base import Capability, CapabilityError


@dataclass(frozen=True)
class CapabilityMetadata:
    name: str
    namespace: str
    version: str
    description: str
    tags: list[str]


@dataclass(frozen=True)
class CapabilityRegistration:
    capability_cls: type[Capability]
    metadata: CapabilityMetadata


class CapabilityRegistry:
    """
    Central registry for all agent capabilities.
    """

    def __init__(self) -> None:
        self._registry: dict[str, CapabilityRegistration] = {}

    def register(
        self,
        capability_cls: type[Capability],
        *,
        name: str | None = None,
        namespace: str = "default",
        version: str = "1.0.0",
        description: str = "",
        tags: list[str] | None = None,
    ) -> None:
        capability_name = name or getattr(capability_cls, "name", None)

        if not capability_name:
            raise CapabilityError("Capability must define a 'name' attribute.")

        if capability_name in self._registry:
            raise ValueError(f"Capability '{capability_name}' already registered.")

        metadata = CapabilityMetadata(
            name=capability_name,
            namespace=namespace,
            version=version,
            description=description,
            tags=list(tags or []),
        )
        self._registry[capability_name] = CapabilityRegistration(
            capability_cls=capability_cls,
            metadata=metadata,
        )
        capability_cls.name = capability_name

    def get(self, name: str) -> type[Capability]:
        if name not in self._registry:
            raise CapabilityError(f"Capability '{name}' is not registered.")

        return self._registry[name].capability_cls

    def list(self) -> dict[str, type[Capability]]:
        return {name: registration.capability_cls for name, registration in self._registry.items()}

    def get_metadata(self, name: str) -> CapabilityMetadata:
        if name not in self._registry:
            raise CapabilityError(f"Capability '{name}' is not registered.")
        return self._registry[name].metadata

    def list_metadata(self) -> dict[str, CapabilityMetadata]:
        return {name: registration.metadata for name, registration in self._registry.items()}

    def entries(self) -> list[CapabilityRegistration]:
        return [self._registry[name] for name in sorted(self._registry)]
