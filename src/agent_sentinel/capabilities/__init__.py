from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar, cast

from .base import Capability, CapabilityError, CapabilitySpec, Result
from .registry import CapabilityRegistry

registry = CapabilityRegistry()

CapabilityClass = TypeVar("CapabilityClass", bound=type[Capability])


def register_capability(
    capability_cls: CapabilityClass | None = None,
    *,
    id: str | None = None,
    name: str | None = None,
    namespace: str | None = None,
    version: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
    schema: object | None = None,
    entrypoint: str | None = None,
) -> CapabilityClass | Callable[[CapabilityClass], CapabilityClass]:
    """
    Decorator for auto-registering capabilities.
    """

    def _decorate(cls: CapabilityClass) -> CapabilityClass:
        registry.register(
            cls,
            capability_id=id,
            name=name,
            namespace=namespace,
            version=version,
            description=description,
            tags=tags,
            schema=schema,
            entrypoint=entrypoint,
        )
        return cls

    if capability_cls is None:
        return _decorate
    return _decorate(cast(CapabilityClass, capability_cls))


def register(capability_cls: CapabilityClass) -> CapabilityClass:
    """
    Backward-compatible decorator alias.
    """

    return cast(CapabilityClass, register_capability(capability_cls))


__all__ = [
    "Capability",
    "CapabilityError",
    "CapabilitySpec",
    "Result",
    "registry",
    "register",
    "register_capability",
]
