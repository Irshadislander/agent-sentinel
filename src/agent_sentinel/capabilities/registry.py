from __future__ import annotations

import builtins
import re
from dataclasses import dataclass
from typing import Any

from .base import Capability, CapabilityError, CapabilitySpec


@dataclass(frozen=True)
class CapabilityMetadata:
    id: str
    name: str
    namespace: str
    version: str
    description: str
    tags: list[str]


@dataclass(frozen=True)
class CapabilityRegistration:
    capability_cls: type[Capability]
    spec: CapabilitySpec
    metadata: CapabilityMetadata


_SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
_JSON_SCHEMA_HINTS = {
    "$schema",
    "$id",
    "$defs",
    "definitions",
    "type",
    "properties",
    "required",
    "items",
    "allOf",
    "anyOf",
    "oneOf",
    "not",
}


def _is_semver(value: str) -> bool:
    return bool(_SEMVER_RE.fullmatch(value))


def _require_nonempty_string(value: object, *, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field} is required")
    return normalized


def _normalize_capability_id(value: object) -> str:
    capability_id = _require_nonempty_string(value, field="capability id")
    if any(character.isspace() for character in capability_id):
        raise ValueError("capability id must not contain whitespace")
    return capability_id


def _coerce_schema(value: Any) -> dict[str, Any]:
    schema_obj = value
    if hasattr(schema_obj, "model_json_schema") and callable(schema_obj.model_json_schema):
        schema_obj = schema_obj.model_json_schema()
    elif hasattr(schema_obj, "schema") and callable(schema_obj.schema):
        schema_obj = schema_obj.schema()

    if not isinstance(schema_obj, dict):
        raise ValueError(
            "schema must be a JSONSchema dictionary or a model convertible to JSONSchema"
        )
    if not schema_obj:
        raise ValueError("schema must not be empty")
    if not any(key in schema_obj for key in _JSON_SCHEMA_HINTS):
        raise ValueError("schema does not look like a JSONSchema object")
    return schema_obj


class CapabilityRegistry:
    """
    Central registry for all agent capabilities.
    """

    def __init__(self) -> None:
        self._registry: dict[str, CapabilityRegistration] = {}
        self._ids: dict[str, str] = {}

    def register(
        self,
        capability_cls: type[Capability],
        *,
        capability_id: str | None = None,
        name: str | None = None,
        namespace: str | None = None,
        version: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        schema: Any = None,
        entrypoint: str | None = None,
    ) -> None:
        existing_spec = getattr(capability_cls, "spec", None)
        spec = existing_spec if isinstance(existing_spec, CapabilitySpec) else None

        capability_name = (
            name or (spec.name if spec else None) or getattr(capability_cls, "name", None)
        )
        if not capability_name:
            raise CapabilityError("Capability must define a 'name' attribute.")

        capability_namespace = namespace or capability_cls.__module__.replace(":", ".")
        capability_version = version or (spec.version if spec else None) or "1.0.0"
        capability_description = (
            description
            or (spec.description if spec else None)
            or (capability_cls.__doc__.strip() if capability_cls.__doc__ else capability_name)
        )
        capability_tags = list(tags or [])
        capability_entrypoint = (
            entrypoint
            or (spec.entrypoint if spec else None)
            or f"{capability_cls.__module__}:{capability_cls.__qualname__}"
        )
        capability_schema = (
            schema if schema is not None else (spec.schema if spec else {"type": "object"})
        )
        capability_schema = _coerce_schema(capability_schema)
        if capability_id is not None:
            capability_unique_id_raw = capability_id
        elif spec is not None:
            capability_unique_id_raw = spec.id
        else:
            capability_unique_id_raw = f"{capability_namespace}:{capability_name}"
        capability_unique_id = _normalize_capability_id(capability_unique_id_raw)
        capability_namespace = _require_nonempty_string(capability_namespace, field="namespace")
        capability_description = _require_nonempty_string(
            capability_description, field="description"
        )

        if not _is_semver(capability_version):
            raise ValueError(f"version must be SemVer (x.y.z): {capability_version}")
        if not all(isinstance(tag, str) and tag for tag in capability_tags):
            raise ValueError("tags must contain non-empty strings")

        if capability_name in self._registry:
            raise ValueError(f"Capability '{capability_name}' already registered.")
        if capability_unique_id in self._ids:
            existing_name = self._ids[capability_unique_id]
            raise ValueError(
                f"Capability id '{capability_unique_id}' already registered by '{existing_name}'."
            )

        metadata = CapabilityMetadata(
            id=capability_unique_id,
            name=capability_name,
            namespace=capability_namespace,
            version=capability_version,
            description=capability_description,
            tags=capability_tags,
        )
        capability_spec = CapabilitySpec(
            id=capability_unique_id,
            name=capability_name,
            version=capability_version,
            description=capability_description,
            schema=capability_schema,
            entrypoint=capability_entrypoint,
        )
        self._registry[capability_name] = CapabilityRegistration(
            capability_cls=capability_cls,
            spec=capability_spec,
            metadata=metadata,
        )
        self._ids[capability_unique_id] = capability_name
        capability_cls.name = capability_name
        capability_cls.spec = capability_spec

    def get(self, name: str) -> type[Capability]:
        if name not in self._registry:
            raise CapabilityError(f"Capability '{name}' is not registered.")

        return self._registry[name].capability_cls

    def get_by_id(self, capability_id: str) -> type[Capability]:
        if capability_id not in self._ids:
            raise CapabilityError(f"Capability id '{capability_id}' is not registered.")
        return self.get(self._ids[capability_id])

    def list(self) -> dict[str, type[Capability]]:
        return {
            registration.metadata.name: registration.capability_cls
            for registration in self.entries()
        }

    def get_metadata(self, name: str) -> CapabilityMetadata:
        if name not in self._registry:
            raise CapabilityError(f"Capability '{name}' is not registered.")
        return self._registry[name].metadata

    def list_metadata(self) -> dict[str, CapabilityMetadata]:
        return {
            registration.metadata.name: registration.metadata for registration in self.entries()
        }

    def get_spec(self, name: str) -> CapabilitySpec:
        if name not in self._registry:
            raise CapabilityError(f"Capability '{name}' is not registered.")
        return self._registry[name].spec

    def get_spec_by_id(self, capability_id: str) -> CapabilitySpec:
        if capability_id not in self._ids:
            raise CapabilityError(f"Capability id '{capability_id}' is not registered.")
        return self.get_spec(self._ids[capability_id])

    def list_specs(self) -> dict[str, CapabilitySpec]:
        return {registration.metadata.name: registration.spec for registration in self.entries()}

    def entries(self) -> builtins.list[CapabilityRegistration]:
        registrations = list(self._registry.values())
        registrations.sort(key=lambda registration: registration.spec.id)
        return registrations
