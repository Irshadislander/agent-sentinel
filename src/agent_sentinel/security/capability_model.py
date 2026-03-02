from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CapabilityCategory(StrEnum):
    FILESYSTEM = "filesystem"
    NETWORK = "network"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class Capability:
    name: str
    category: CapabilityCategory
    risk: RiskLevel
    description: str = ""


class CapabilityRegistry:
    def __init__(self) -> None:
        self._by_name: dict[str, Capability] = {}

    def register(self, cap: Capability) -> None:
        self._by_name[cap.name] = cap

    def get(self, name: str) -> Capability | None:
        return self._by_name.get(name)

    def is_known(self, name: str) -> bool:
        return name in self._by_name

    def all_names(self) -> set[str]:
        return set(self._by_name.keys())

    def all(self) -> list[Capability]:
        return list(self._by_name.values())
