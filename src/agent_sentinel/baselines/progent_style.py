from __future__ import annotations

from dataclasses import dataclass
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

_SENSITIVE_KEYS = ("secret", "token", "password", "credential", "key")


@dataclass(frozen=True, slots=True)
class Rule:
    action: str
    tool_name: str
    path_prefix: str | None = None
    allow_hosts: tuple[str, ...] = ()
    deny_sensitive_payload: bool = False


class ProgentStyleExecutor:
    def __init__(
        self,
        *,
        policy: dict[str, Any],
        tools: dict[str, ToolFn],
        recorder: RecorderLike,
        rules: list[Rule] | None = None,
    ) -> None:
        allowlist_domains = tuple(allowlist_domains_from_policy(policy))
        self._rules = list(
            rules
            or [
                Rule(action="allow", tool_name="read_text", path_prefix="public/"),
                Rule(action="deny", tool_name="read_text"),
                Rule(action="allow", tool_name="write_text", path_prefix="workspace/"),
                Rule(action="deny", tool_name="write_text"),
                Rule(action="allow", tool_name="http_get", allow_hosts=allowlist_domains),
                Rule(action="deny", tool_name="http_get"),
                Rule(
                    action="allow",
                    tool_name="http_post",
                    allow_hosts=allowlist_domains,
                    deny_sensitive_payload=True,
                ),
                Rule(action="deny", tool_name="http_post"),
            ]
        )
        self._allowlist_domains = list(allowlist_domains)
        self._base_dir = Path(policy.get("base_dir", "."))
        self._tools = dict(tools)
        self._recorder = recorder

    def execute(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        normalized = canonical_tool_name(tool_name)
        for rule in self._rules:
            if not self._matches(rule=rule, tool_name=normalized, args=args):
                continue
            if rule.action == "deny":
                deny_tool(
                    recorder=self._recorder,
                    tool_name=tool_name,
                    args=args,
                    reason=f"denied by Progent-style rule for {normalized}",
                )

            validation = self._validate_allowed_rule(tool_name=normalized, args=args)
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

        deny_tool(
            recorder=self._recorder,
            tool_name=tool_name,
            args=args,
            reason=f"default deny in Progent-style policy: {normalized}",
        )

    def _matches(self, *, rule: Rule, tool_name: str, args: dict[str, Any]) -> bool:
        if rule.tool_name != tool_name:
            return False

        if rule.path_prefix is not None:
            path = str(args.get("path", "")).replace("\\", "/")
            if not path.startswith(rule.path_prefix):
                return False

        if rule.allow_hosts:
            _, host = validators.parse_url(str(args.get("url", "")))
            if not host or not any(
                host == domain.lower().lstrip(".")
                or host.endswith(f".{domain.lower().lstrip('.')}")
                for domain in rule.allow_hosts
            ):
                return False

        return not (
            rule.deny_sensitive_payload and self._contains_sensitive_payload(args.get("json_body"))
        )

    def _validate_allowed_rule(
        self, *, tool_name: str, args: dict[str, Any]
    ) -> validators.ValidationResult:
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
                allow_post=True,
            )
        return validators.ValidationResult(False, f"unsupported tool: {tool_name}")

    @classmethod
    def _contains_sensitive_payload(cls, value: Any) -> bool:
        if isinstance(value, dict):
            for key, nested in value.items():
                if any(marker in str(key).lower() for marker in _SENSITIVE_KEYS):
                    return True
                if cls._contains_sensitive_payload(nested):
                    return True
            return False
        if isinstance(value, list):
            return any(cls._contains_sensitive_payload(item) for item in value)
        if isinstance(value, tuple):
            return any(cls._contains_sensitive_payload(item) for item in value)
        return False
