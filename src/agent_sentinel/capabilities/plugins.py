from __future__ import annotations

import importlib.metadata as importlib_metadata
from collections.abc import Callable
from typing import Any

from . import registry
from .base import Capability

ENTRYPOINT_GROUP = "agent_sentinel.capabilities"
_LOADED_ENTRYPOINTS: set[str] = set()


def discover_entrypoint_capabilities() -> list[importlib_metadata.EntryPoint]:
    raw_entry_points = importlib_metadata.entry_points()
    if hasattr(raw_entry_points, "select"):
        selected = raw_entry_points.select(group=ENTRYPOINT_GROUP)
        return sorted(selected, key=lambda entry: entry.name)

    legacy_get = getattr(raw_entry_points, "get", None)
    if callable(legacy_get):
        legacy = legacy_get(ENTRYPOINT_GROUP, ())
        return sorted(legacy, key=lambda entry: entry.name)

    return []


def _register_plugin_object(plugin_object: object) -> None:
    if isinstance(plugin_object, type) and issubclass(plugin_object, Capability):
        registry.register(plugin_object)
        return

    if isinstance(plugin_object, Capability):
        registry.register(type(plugin_object))
        return

    if callable(plugin_object):
        produced = plugin_object()
        if produced is None:
            return
        _register_plugin_object(produced)
        return

    if isinstance(plugin_object, (list, tuple, set)):
        for item in plugin_object:
            _register_plugin_object(item)
        return

    raise ValueError(
        "Plugin object must be a Capability class/instance, callable, or collection of capabilities."
    )


def load_capabilities(
    allowed: list[str] | None = None,
    *,
    strict: bool = False,
    warn: Callable[[str], None] | None = None,
) -> list[str]:
    loaded: list[str] = []
    allowset = set(allowed) if allowed is not None else None

    def _warn(message: str) -> None:
        if warn is not None:
            warn(message)

    for entrypoint in discover_entrypoint_capabilities():
        if allowset is not None and entrypoint.name not in allowset:
            continue

        identifier = f"{entrypoint.group}:{entrypoint.name}={entrypoint.value}"
        if identifier in _LOADED_ENTRYPOINTS:
            continue

        try:
            plugin_object: Any = entrypoint.load()
            _register_plugin_object(plugin_object)
            _LOADED_ENTRYPOINTS.add(identifier)
            loaded.append(entrypoint.name)
        except Exception as exc:
            message = (
                f"failed to load plugin '{entrypoint.name}' from '{entrypoint.value}': "
                f"{type(exc).__name__}: {exc}"
            )
            if strict:
                raise RuntimeError(message) from exc
            _warn(message)

    return loaded
