from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .enforcer import EnforcementContext, enforce_request


@dataclass(frozen=True)
class ToolCall:
    tool_name: str
    capability: str
    fn: Callable[..., Any]


class AgentRuntime:
    """
    Minimal simulation runtime for tool-using agents.

    Agent chooses a tool -> runtime enforces policy -> tool executes.
    """

    def __init__(self, policy: Any) -> None:
        self._policy = policy
        self._tools: dict[str, ToolCall] = {}

    def register_tool(self, tool: ToolCall) -> None:
        self._tools[tool.tool_name] = tool

    def call(self, tool_name: str, *args: Any, **kwargs: Any) -> Any:
        if tool_name not in self._tools:
            raise KeyError(f"Tool not registered: {tool_name}")

        tool = self._tools[tool_name]

        enforce_request(
            tool.capability,
            self._policy,
            context=EnforcementContext(tool=tool.tool_name),
        )

        return tool.fn(*args, **kwargs)
