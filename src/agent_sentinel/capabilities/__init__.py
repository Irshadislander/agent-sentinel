from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from .base import Capability
from .registry import CapabilityRegistry

registry = CapabilityRegistry()

CapabilityClass = TypeVar("CapabilityClass", bound=type[Capability])


def register_capability(
    capability_cls: CapabilityClass | None = None,
    *,
    name: str | None = None,
    namespace: str = "default",
    version: str = "1.0.0",
    description: str = "",
    tags: list[str] | None = None,
) -> CapabilityClass | Callable[[CapabilityClass], CapabilityClass]:
    """
    Decorator for auto-registering capabilities.
    """

    def _decorate(cls: CapabilityClass) -> CapabilityClass:
        registry.register(
            cls,
            name=name,
            namespace=namespace,
            version=version,
            description=description,
            tags=tags,
        )
        return cls

    if capability_cls is None:
        return _decorate
    return _decorate(capability_cls)


def register(capability_cls: CapabilityClass) -> CapabilityClass:
    """
    Backward-compatible decorator alias.
    """

    return register_capability(capability_cls)


__all__ = ["registry", "register", "register_capability"]
