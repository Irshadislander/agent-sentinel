from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from agent_sentinel.cli_exit_codes import ExitCode


class CapabilityError(Exception):
    """Raised when a capability fails."""


@dataclass(frozen=True)
class CapabilitySpec:
    id: str
    name: str
    version: str
    description: str
    schema: dict[str, Any]
    entrypoint: str


@dataclass(frozen=True)
class Result:
    ok: bool
    code: ExitCode
    data: dict[str, Any] | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None


class Capability(ABC):
    """
    Base class for all capabilities.

    A capability is a self-contained unit of agent functionality.
    """

    name: str
    spec: CapabilitySpec

    @abstractmethod
    def execute(self, payload: dict[str, Any]) -> Result:
        """
        Execute the capability.

        Args:
            payload: Input data

        Returns:
            Structured capability result.
        """
        raise NotImplementedError
