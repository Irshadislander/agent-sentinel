from __future__ import annotations

from dataclasses import dataclass
import ipaddress
from pathlib import PurePosixPath
from typing import Any
from urllib.parse import urlparse

from agent_sentinel.security.capabilities import (
    FS_READ_PRIVATE,
    FS_READ_PUBLIC,
    FS_WRITE_WORKSPACE,
    NET_EXTERNAL,
    NET_HTTP_GET,
    NET_HTTP_POST,
    NET_INTERNAL,
)

ALLOW = "ALLOW"
DENY = "DENY"
REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
ALLOW_WITH_REDACTION = "ALLOW_WITH_REDACTION"

_SENSITIVE_TOKENS = ("email", "token", "secret", "password")
_HTTP_GET_NAMES = {"http.get", "http_get", "tools.http.get", "http_tool.http_get"}
_HTTP_POST_NAMES = {"http.post", "http_post", "tools.http.post", "http_tool.http_post"}
_FS_READ_NAMES = {"fs.read", "fs.read_text", "read_text", "fs_tool.read_text"}
_FS_WRITE_NAMES = {"fs.write", "fs.write_text", "write_text", "fs_tool.write_text"}


@dataclass(slots=True)
class PolicyDecision:
    verdict: str
    reason: str
    redactions: dict[str, Any] | None = None


class PolicyEngine:
    def __init__(self, policy: dict[str, Any] | None):
        self._policy = policy or {}
        internal_domains = self._policy.get("internal_domains", ())
        self._internal_domains = tuple(str(domain).lower().lstrip(".") for domain in internal_domains)

    def decide(self, *, tool_name: str, args: dict[str, Any], caps: set[str]) -> PolicyDecision:
        normalized_tool = tool_name.strip().lower()

        if self._is_http_get(normalized_tool):
            return self._decide_http(method="GET", args=args, caps=caps)
        if self._is_http_post(normalized_tool):
            return self._decide_http(method="POST", args=args, caps=caps)
        if self._is_fs_read(normalized_tool):
            return self._decide_fs_read(args=args, caps=caps)
        if self._is_fs_write(normalized_tool):
            return self._decide_fs_write(args=args, caps=caps)

        return PolicyDecision(DENY, f"unknown tool denied by default: {tool_name}")

    def _decide_http(self, *, method: str, args: dict[str, Any], caps: set[str]) -> PolicyDecision:
        url = args.get("url")
        if not isinstance(url, str) or not url:
            return PolicyDecision(DENY, "missing required http url")

        if method == "GET" and NET_HTTP_GET not in caps:
            return PolicyDecision(DENY, f"{method} denied: missing capability {NET_HTTP_GET}")
        if method == "POST" and NET_HTTP_POST not in caps:
            return PolicyDecision(DENY, f"{method} denied: missing capability {NET_HTTP_POST}")

        is_external = self._is_external_destination(url)
        if is_external and NET_EXTERNAL not in caps:
            return PolicyDecision(DENY, f"{method} denied: external network requires {NET_EXTERNAL}")
        if not is_external and NET_INTERNAL not in caps:
            return PolicyDecision(DENY, f"{method} denied: internal network requires {NET_INTERNAL}")

        if is_external and self._contains_sensitive_key(args):
            return PolicyDecision(
                REQUIRE_APPROVAL,
                "external destination with sensitive payload requires explicit approval",
            )

        return self._allow_or_redact(args=args, reason=f"{method} allowed by policy")

    def _decide_fs_read(self, *, args: dict[str, Any], caps: set[str]) -> PolicyDecision:
        scope = self._path_scope(args.get("path"))
        if scope == "public":
            if FS_READ_PUBLIC in caps:
                return self._allow_or_redact(
                    args=args,
                    reason=f"file read allowed under public/ with {FS_READ_PUBLIC}",
                )
            return PolicyDecision(DENY, f"file read denied: missing capability {FS_READ_PUBLIC}")
        if scope == "private":
            if FS_READ_PRIVATE in caps:
                return self._allow_or_redact(
                    args=args,
                    reason=f"file read allowed under private/ with {FS_READ_PRIVATE}",
                )
            return PolicyDecision(DENY, f"file read denied: missing capability {FS_READ_PRIVATE}")
        if scope == "invalid":
            return PolicyDecision(DENY, "file read denied: invalid path")
        return PolicyDecision(DENY, "file read denied: path must be under public/ or private/")

    def _decide_fs_write(self, *, args: dict[str, Any], caps: set[str]) -> PolicyDecision:
        scope = self._path_scope(args.get("path"))
        if scope == "workspace":
            if FS_WRITE_WORKSPACE in caps:
                return self._allow_or_redact(
                    args=args,
                    reason=f"file write allowed under workspace/ with {FS_WRITE_WORKSPACE}",
                )
            return PolicyDecision(DENY, f"file write denied: missing capability {FS_WRITE_WORKSPACE}")
        if scope == "invalid":
            return PolicyDecision(DENY, "file write denied: invalid path")
        return PolicyDecision(DENY, "file write denied: only workspace/ is writable")

    @staticmethod
    def _is_http_get(tool_name: str) -> bool:
        return tool_name in _HTTP_GET_NAMES

    @staticmethod
    def _is_http_post(tool_name: str) -> bool:
        return tool_name in _HTTP_POST_NAMES

    @staticmethod
    def _is_fs_read(tool_name: str) -> bool:
        return tool_name in _FS_READ_NAMES

    @staticmethod
    def _is_fs_write(tool_name: str) -> bool:
        return tool_name in _FS_WRITE_NAMES

    def _is_external_destination(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return True

        host = (parsed.hostname or "").lower()
        if not host:
            return True
        if host == "localhost" or host.endswith(".local") or host.endswith(".internal"):
            return False
        if self._is_internal_domain(host):
            return False

        try:
            ip = ipaddress.ip_address(host)
        except ValueError:
            return True

        if ip.is_loopback or ip.is_private or ip.is_link_local:
            return False
        return True

    def _is_internal_domain(self, host: str) -> bool:
        for domain in self._internal_domains:
            if host == domain or host.endswith(f".{domain}"):
                return True
        return False

    @staticmethod
    def _contains_sensitive_key(value: Any) -> bool:
        if isinstance(value, dict):
            for key, nested in value.items():
                lowered = str(key).lower()
                if any(token in lowered for token in _SENSITIVE_TOKENS):
                    return True
                if PolicyEngine._contains_sensitive_key(nested):
                    return True
            return False
        if isinstance(value, list):
            return any(PolicyEngine._contains_sensitive_key(item) for item in value)
        if isinstance(value, tuple):
            return any(PolicyEngine._contains_sensitive_key(item) for item in value)
        return False

    def _allow_or_redact(self, *, args: dict[str, Any], reason: str) -> PolicyDecision:
        if not self._policy.get("auto_redact_args", False):
            return PolicyDecision(ALLOW, reason)

        redactions = self._collect_redactions(args)
        if redactions:
            return PolicyDecision(
                ALLOW_WITH_REDACTION,
                "allowed with argument redactions",
                redactions=redactions,
            )
        return PolicyDecision(ALLOW, reason)

    @staticmethod
    def _collect_redactions(value: Any, prefix: str = "") -> dict[str, str]:
        redactions: dict[str, str] = {}
        if isinstance(value, dict):
            for key, nested in value.items():
                key_str = str(key)
                path = f"{prefix}.{key_str}" if prefix else key_str
                lowered = key_str.lower()
                if any(token in lowered for token in _SENSITIVE_TOKENS):
                    redactions[path] = "***"
                else:
                    redactions.update(PolicyEngine._collect_redactions(nested, path))
        elif isinstance(value, list):
            for item in value:
                redactions.update(PolicyEngine._collect_redactions(item, prefix))
        elif isinstance(value, tuple):
            for item in value:
                redactions.update(PolicyEngine._collect_redactions(item, prefix))
        return redactions

    @staticmethod
    def _path_scope(path_value: Any) -> str:
        if not isinstance(path_value, str) or not path_value:
            return "invalid"

        candidate = path_value.replace("\\", "/")
        posix = PurePosixPath(candidate)
        if posix.is_absolute():
            return "invalid"

        parts = [part for part in posix.parts if part not in ("", ".")]
        if not parts:
            return "invalid"
        if any(part == ".." for part in parts):
            return "invalid"

        root = parts[0]
        if root == "public":
            return "public"
        if root == "private":
            return "private"
        if root == "workspace":
            return "workspace"
        return "other"
