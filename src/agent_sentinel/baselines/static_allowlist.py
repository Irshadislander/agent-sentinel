from __future__ import annotations

from typing import Any

from . import RecorderLike, ToolFn, canonical_tool_name, deny_tool, execute_tool

_DEFAULT_ALLOWED_TOOLS = {"read_text", "write_text", "http_get"}


class StaticAllowlistExecutor:
    def __init__(
        self,
        *,
        tools: dict[str, ToolFn],
        recorder: RecorderLike,
        allowed_tools: set[str] | None = None,
    ) -> None:
        selected = allowed_tools or _DEFAULT_ALLOWED_TOOLS
        self._allowed_tools = {canonical_tool_name(tool_name) for tool_name in selected}
        self._tools = dict(tools)
        self._recorder = recorder

    def execute(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        if canonical_tool_name(tool_name) not in self._allowed_tools:
            deny_tool(
                recorder=self._recorder,
                tool_name=tool_name,
                args=args,
                reason=f"tool denied by static allowlist: {tool_name}",
            )

        return execute_tool(
            recorder=self._recorder,
            tools=self._tools,
            tool_name=tool_name,
            args=args,
        )
