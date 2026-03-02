from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CapabilityError(Exception):
    """Raised when a capability fails."""


class Capability(ABC):
    """
    Base class for all capabilities.

    A capability is a self-contained unit of agent functionality.
    """

    name: str

    @abstractmethod
    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the capability.

        Args:
            payload: Input data

        Returns:
            Result dictionary
        """
        raise NotImplementedError
