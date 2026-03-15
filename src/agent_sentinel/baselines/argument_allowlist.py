from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_sentinel.security import validators

from . import (
    RecorderLike,
    ToolFn,
    allowlist_domains_from_policy,
    canonical_tool_name,
    deny_tool,
    execute_tool,
    validate_workspace_write,
)

_DEFAULT_ALLOWED_TOOLS = {"read_text", "write_text", "http_get", "http_post"}


class ArgumentAllowlistExecutor:
    def __init__(
        self,
        *,
        policy: dict[str, Any],
        tools: dict[str, ToolFn],
        recorder: RecorderLike,
        allowed_tools: set[str] | None = None,
    ) -> None:
        selected = allowed_tools or _DEFAULT_ALLOWED_TOOLS
        self._allowed_tools = {canonical_tool_name(tool_name) for tool_name in selected}
        self._allowlist_domains = allowlist_domains_from_policy(policy)
        self._base_dir = Path(policy.get("base_dir", "."))
        self._tools = dict(tools)
        self._recorder = recorder

    def execute(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        normalized = canonical_tool_name(tool_name)
        if normalized not in self._allowed_tools:
            deny_tool(
                recorder=self._recorder,
                tool_name=tool_name,
                args=args,
                reason=f"tool denied by argument allowlist: {tool_name}",
            )

        validation = self._validate(tool_name=normalized, args=args)
        if not validation.allowed:
            deny_tool(
                recorder=self._recorder,
                tool_name=tool_name,
                args=args,
                reason=validation.reason,
            )

        return execute_tool(
            recorder=self._recorder,
            tools=self._tools,
            tool_name=tool_name,
            args=args,
        )

    def _validate(self, *, tool_name: str, args: dict[str, Any]) -> validators.ValidationResult:
        if tool_name == "read_text":
            return validators.validate_fs_read(
                str(args.get("path", "")),
                base_dir=self._base_dir,
                allow_private=False,
            )

        if tool_name == "write_text":
            return validate_workspace_write(
                str(args.get("path", "")),
                base_dir=self._base_dir,
            )

        if tool_name == "http_get":
            return validators.validate_http_request(
                method="GET",
                url=str(args.get("url", "")),
                allowlist_domains=self._allowlist_domains,
                allow_post=False,
            )

        if tool_name == "http_post":
            return validators.validate_http_request(
                method="POST",
                url=str(args.get("url", "")),
                allowlist_domains=self._allowlist_domains,
                allow_post=False,
            )

        return validators.ValidationResult(False, f"tool denied by argument allowlist: {tool_name}")
