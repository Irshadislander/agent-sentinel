from __future__ import annotations

from typing import Any

from . import RecorderLike, ToolFn, execute_tool


class NoProtectionExecutor:
    def __init__(
        self,
        *,
        tools: dict[str, ToolFn],
        recorder: RecorderLike,
    ) -> None:
        self._tools = dict(tools)
        self._recorder = recorder

    def execute(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        return execute_tool(
            recorder=self._recorder,
            tools=self._tools,
            tool_name=tool_name,
            args=args,
        )
