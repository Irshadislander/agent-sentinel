from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any, Protocol

from agent_sentinel.security import validators

if TYPE_CHECKING:
    from .argument_allowlist import ArgumentAllowlistExecutor
    from .no_audit import NoAuditExecutor
    from .no_protection import NoProtectionExecutor
    from .progent_style import ProgentStyleExecutor
    from .static_allowlist import StaticAllowlistExecutor
    from .validator_only import ValidatorOnlyExecutor

ToolFn = Callable[..., Any]

_TOOL_ALIASES = {
    "fs.read": "read_text",
    "fs_read": "read_text",
    "fs.read_text": "read_text",
    "fs_tool.read_text": "read_text",
    "read_text": "read_text",
    "fs.write": "write_text",
    "fs_write": "write_text",
    "fs.write_text": "write_text",
    "fs_tool.write_text": "write_text",
    "write_text": "write_text",
    "http.get": "http_get",
    "http_get": "http_get",
    "tools.http.get": "http_get",
    "http_tool.http_get": "http_get",
    "http.post": "http_post",
    "http_post": "http_post",
    "tools.http.post": "http_post",
    "http_tool.http_post": "http_post",
}


class RecorderLike(Protocol):
    def append(self, event_type: str, payload: dict[str, Any]) -> None: ...


class ExecutorLike(Protocol):
    def execute(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]: ...


class NoopRecorder:
    def append(self, event_type: str, payload: dict[str, Any]) -> None:
        del event_type, payload
        return None


_LAZY_EXPORTS = {
    "ArgumentAllowlistExecutor": ".argument_allowlist",
    "NoAuditExecutor": ".no_audit",
    "NoProtectionExecutor": ".no_protection",
    "ProgentStyleExecutor": ".progent_style",
    "StaticAllowlistExecutor": ".static_allowlist",
    "ValidatorOnlyExecutor": ".validator_only",
}


def canonical_tool_name(tool_name: str) -> str:
    normalized = tool_name.strip().lower()
    return _TOOL_ALIASES.get(normalized, normalized)


def granted_capabilities_from_policy(policy: dict[str, Any]) -> set[str]:
    capabilities = policy.get("capabilities")
    if isinstance(capabilities, dict):
        return {str(capability) for capability, enabled in capabilities.items() if bool(enabled)}

    granted = policy.get("granted_caps", [])
    if isinstance(granted, list):
        return {str(capability) for capability in granted}
    return set()


def allowlist_domains_from_policy(policy: dict[str, Any]) -> list[str]:
    raw = policy.get("allowlist_domains", [])
    if not isinstance(raw, list):
        return []
    return [str(domain) for domain in raw]


def validate_workspace_write(
    path: str,
    *,
    base_dir: str | Path = ".",
) -> validators.ValidationResult:
    if not isinstance(path, str) or not path:
        return validators.ValidationResult(False, "invalid fs path")

    posix_path = PurePosixPath(path.replace("\\", "/"))
    if posix_path.is_absolute():
        return validators.ValidationResult(False, "absolute paths are not allowed")
    if any(part == ".." for part in posix_path.parts):
        return validators.ValidationResult(False, "path traversal is not allowed")

    root = Path(base_dir).resolve()
    candidate = (root / posix_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return validators.ValidationResult(False, "path escapes base_dir")

    parts = [part for part in posix_path.parts if part not in ("", ".")]
    if not parts or parts[0] != "workspace":
        return validators.ValidationResult(False, "only workspace/ paths are writable")
    return validators.ValidationResult(True, "ok")


def deny_tool(
    *,
    recorder: RecorderLike,
    tool_name: str,
    args: dict[str, Any],
    reason: str,
) -> None:
    recorder.append("tool.call.requested", {"tool_name": tool_name, "args": args})
    recorder.append("tool.call.blocked", {"tool_name": tool_name, "reason": reason})
    raise PermissionError(reason)


def execute_tool(
    *,
    recorder: RecorderLike,
    tools: dict[str, ToolFn],
    tool_name: str,
    args: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(args, dict):
        raise TypeError("args must be a dictionary")

    recorder.append("tool.call.requested", {"tool_name": tool_name, "args": args})
    tool = tools.get(tool_name)
    if tool is None:
        recorder.append("tool.call.blocked", {"tool_name": tool_name, "reason": "unknown tool"})
        raise PermissionError(f"unknown tool: {tool_name}")

    result = tool(**args)
    if not isinstance(result, dict):
        recorder.append(
            "tool.call.failed",
            {"tool_name": tool_name, "reason": "tool result must be a dictionary"},
        )
        raise TypeError("tool result must be a dictionary")

    recorder.append("tool.call.completed", {"tool_name": tool_name})
    return result


def __getattr__(name: str) -> Any:
    module_name = _LAZY_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(module_name, __name__)
    return getattr(module, name)


__all__ = [
    "ArgumentAllowlistExecutor",
    "ExecutorLike",
    "NoAuditExecutor",
    "NoProtectionExecutor",
    "NoopRecorder",
    "ProgentStyleExecutor",
    "RecorderLike",
    "StaticAllowlistExecutor",
    "ToolFn",
    "ValidatorOnlyExecutor",
    "allowlist_domains_from_policy",
    "canonical_tool_name",
    "deny_tool",
    "execute_tool",
    "granted_capabilities_from_policy",
    "validate_workspace_write",
]
