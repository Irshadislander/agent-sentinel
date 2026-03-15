from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_sentinel.security import validators
from agent_sentinel.security.capabilities import FS_READ_PRIVATE, NET_HTTP_POST

from . import (
    RecorderLike,
    ToolFn,
    allowlist_domains_from_policy,
    canonical_tool_name,
    deny_tool,
    execute_tool,
    granted_capabilities_from_policy,
)


class ValidatorOnlyExecutor:
    def __init__(
        self,
        *,
        policy: dict[str, Any],
        tools: dict[str, ToolFn],
        recorder: RecorderLike,
    ) -> None:
        granted = granted_capabilities_from_policy(policy)
        self._allow_private = FS_READ_PRIVATE in granted
        self._allow_post = NET_HTTP_POST in granted
        self._allowlist_domains = allowlist_domains_from_policy(policy)
        self._base_dir = Path(policy.get("base_dir", "."))
        self._tools = dict(tools)
        self._recorder = recorder

    def execute(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        validation = self._validate(tool_name=tool_name, args=args)
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
        normalized = canonical_tool_name(tool_name)
        if normalized == "read_text":
            return validators.validate_fs_read(
                str(args.get("path", "")),
                base_dir=self._base_dir,
                allow_private=self._allow_private,
            )
        if normalized == "http_get":
            return validators.validate_http_request(
                method="GET",
                url=str(args.get("url", "")),
                allowlist_domains=self._allowlist_domains,
                allow_post=self._allow_post,
            )
        if normalized == "http_post":
            return validators.validate_http_request(
                method="POST",
                url=str(args.get("url", "")),
                allowlist_domains=self._allowlist_domains,
                allow_post=self._allow_post,
            )
        return validators.ValidationResult(True, "ok")
