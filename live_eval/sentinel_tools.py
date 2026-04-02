from __future__ import annotations

import fnmatch
import json
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Literal
from urllib.parse import urlparse

import requests

ALLOW = "ALLOW"
DENY = "DENY"

ToolLogger = Callable[[dict[str, Any]], None]
Decision = Literal["ALLOW", "DENY"]

DEFAULT_POLICY_PATH = Path(__file__).resolve().with_name("policies.json")
DEFAULT_RUNTIME_ROOT = Path(__file__).resolve().parent / "runtime"
DEFAULT_TIMEOUT_S = 10.0
DEFAULT_TEXT_LIMIT = 4000
DEFAULT_BODY_LIMIT = 4000

_LOG = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class PolicyConfig:
    allowed_paths: tuple[str, ...]
    denied_paths: tuple[str, ...]
    allowed_domains: tuple[str, ...]
    denied_domains: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    allowed: bool
    reason: str
    matched_rule: str | None = None


def _load_string_list(raw: Any, field_name: str) -> tuple[str, ...]:
    if raw is None:
        return ()
    if not isinstance(raw, list) or not all(isinstance(item, str) for item in raw):
        raise ValueError(f"{field_name} must be a list of strings")
    return tuple(item.strip() for item in raw if str(item).strip())


def load_policy(policy_path: Path | str = DEFAULT_POLICY_PATH) -> PolicyConfig:
    path = Path(policy_path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("policies.json must contain a JSON object")

    return PolicyConfig(
        allowed_paths=_load_string_list(raw.get("allowed_paths"), "allowed_paths"),
        denied_paths=_load_string_list(raw.get("denied_paths"), "denied_paths"),
        allowed_domains=_load_string_list(raw.get("allowed_domains"), "allowed_domains"),
        denied_domains=_load_string_list(raw.get("denied_domains"), "denied_domains"),
    )


def _normalize_path_text(path: str) -> str:
    return path.replace("\\", "/").strip()


def _normalize_glob(value: str) -> str:
    return _normalize_path_text(value).lower().removeprefix("./")


def _path_matches(candidate: str, pattern: str) -> bool:
    normalized_candidate = _normalize_glob(candidate)
    normalized_pattern = _normalize_glob(pattern)
    if not normalized_pattern:
        return False

    if any(char in normalized_pattern for char in "*?[]"):
        return fnmatch.fnmatchcase(normalized_candidate, normalized_pattern)

    normalized_candidate = normalized_candidate.rstrip("/")
    normalized_pattern = normalized_pattern.rstrip("/")
    return normalized_candidate == normalized_pattern or normalized_candidate.startswith(
        f"{normalized_pattern}/"
    )


def _normalize_domain(domain: str) -> str:
    return domain.strip().lower().rstrip(".")


def _domain_matches(candidate: str, pattern: str) -> bool:
    normalized_candidate = _normalize_domain(candidate)
    normalized_pattern = _normalize_domain(pattern)
    if not normalized_pattern:
        return False

    if normalized_pattern.startswith("*."):
        suffix = normalized_pattern[2:]
        return normalized_candidate == suffix or normalized_candidate.endswith(f".{suffix}")

    if any(char in normalized_pattern for char in "*?[]"):
        return fnmatch.fnmatchcase(normalized_candidate, normalized_pattern)

    return normalized_candidate == normalized_pattern or normalized_candidate.endswith(
        f".{normalized_pattern}"
    )


def _ensure_safe_relative_path(raw_path: str) -> tuple[str, str | None, str | None]:
    candidate = _normalize_path_text(raw_path)
    if not candidate:
        return candidate, None, "invalid path"
    if "://" in candidate:
        return candidate, None, "path must not look like a URL"
    if "\x00" in candidate:
        return candidate, None, "path contains a NUL byte"

    normalized = candidate.replace("\\", "/")
    try:
        posix = PurePosixPath(normalized)
    except Exception:
        return candidate, None, "invalid path"

    if posix.is_absolute():
        return candidate, None, "absolute paths are not allowed"
    if any(part == ".." for part in posix.parts):
        return candidate, None, "path traversal is not allowed"

    rel_path = posix.as_posix()
    if rel_path.startswith("./"):
        rel_path = rel_path[2:]
    return candidate, rel_path, None


def _resolve_runtime_path(base_dir: Path, path: str) -> tuple[Path | None, str | None, str | None]:
    _raw_path, rel_path, error = _ensure_safe_relative_path(path)
    if error is not None:
        return None, None, error

    candidate = (base_dir / rel_path).resolve()
    try:
        candidate.relative_to(base_dir)
    except ValueError:
        return None, None, "path escapes the runtime root"

    return candidate, rel_path, None


def _path_policy_decision(policy: PolicyConfig, rel_path: str) -> PolicyDecision:
    for denied_pattern in policy.denied_paths:
        if _path_matches(rel_path, denied_pattern):
            return PolicyDecision(False, f"path denied by policy: {denied_pattern}", denied_pattern)

    for allowed_pattern in policy.allowed_paths:
        if _path_matches(rel_path, allowed_pattern):
            return PolicyDecision(
                True, f"path allowed by policy: {allowed_pattern}", allowed_pattern
            )

    return PolicyDecision(False, "path not covered by the allowlist")


def _domain_policy_decision(policy: PolicyConfig, host: str) -> PolicyDecision:
    normalized_host = _normalize_domain(host)
    if not normalized_host:
        return PolicyDecision(False, "missing destination host")

    for denied_pattern in policy.denied_domains:
        if _domain_matches(normalized_host, denied_pattern):
            return PolicyDecision(
                False, f"domain denied by policy: {denied_pattern}", denied_pattern
            )

    for allowed_pattern in policy.allowed_domains:
        if _domain_matches(normalized_host, allowed_pattern):
            return PolicyDecision(
                True, f"domain allowed by policy: {allowed_pattern}", allowed_pattern
            )

    return PolicyDecision(False, "domain not covered by the allowlist")


def _truncate_text(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[: max(0, limit - 1)] + "…"


def _result_base(
    *,
    tool_name: str,
    decision: Decision,
    allowed: bool,
    ok: bool,
    reason: str,
    denial_reason: str,
    latency_ms: float,
    error: str = "",
    blocked: bool | None = None,
) -> dict[str, Any]:
    if blocked is None:
        blocked = decision == DENY
    return {
        "tool_name": tool_name,
        "decision": decision,
        "allowed": allowed,
        "blocked": blocked,
        "ok": ok,
        "reason": reason,
        "denial_reason": denial_reason,
        "error": error,
        "latency_ms": round(latency_ms, 3),
    }


class LiveEvalSentinelTools:
    """Policy-mediated file and HTTP tools for live evaluation."""

    def __init__(
        self,
        *,
        policy: PolicyConfig | None = None,
        policy_path: Path | str = DEFAULT_POLICY_PATH,
        base_dir: Path | str = DEFAULT_RUNTIME_ROOT,
        logger: ToolLogger | None = None,
        timeout_s: float = DEFAULT_TIMEOUT_S,
    ) -> None:
        self.policy = policy or load_policy(policy_path)
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._logger = logger
        self._timeout_s = timeout_s
        self._session = requests.Session()

    def _emit(self, record: dict[str, Any]) -> None:
        if self._logger is not None:
            self._logger(record)
            return
        _LOG.debug("%s", json.dumps(record, sort_keys=True, ensure_ascii=False))

    def _finalize(self, record: dict[str, Any]) -> dict[str, Any]:
        self._emit(record)
        return record

    def read_file(self, path: str) -> dict[str, Any]:
        start = time.perf_counter()
        candidate_path, rel_path, path_error = _resolve_runtime_path(self.base_dir, path)
        if path_error is not None or rel_path is None or candidate_path is None:
            latency_ms = (time.perf_counter() - start) * 1000.0
            return self._finalize(
                _result_base(
                    tool_name="read_file",
                    decision=DENY,
                    allowed=False,
                    ok=False,
                    reason=path_error or "invalid path",
                    denial_reason=path_error or "invalid path",
                    latency_ms=latency_ms,
                )
                | {"path": path, "resolved_path": "", "content": "", "bytes": 0}
            )

        policy_decision = _path_policy_decision(self.policy, rel_path)
        if not policy_decision.allowed:
            latency_ms = (time.perf_counter() - start) * 1000.0
            return self._finalize(
                _result_base(
                    tool_name="read_file",
                    decision=DENY,
                    allowed=False,
                    ok=False,
                    reason=policy_decision.reason,
                    denial_reason=policy_decision.reason,
                    latency_ms=latency_ms,
                )
                | {
                    "path": rel_path,
                    "resolved_path": str(candidate_path),
                    "content": "",
                    "bytes": 0,
                }
            )

        try:
            content = candidate_path.read_text(encoding="utf-8", errors="replace")
            ok = True
            error = ""
        except Exception as exc:  # pragma: no cover - exercised in live runs
            content = ""
            ok = False
            error = f"{type(exc).__name__}: {exc}"

        latency_ms = (time.perf_counter() - start) * 1000.0
        record = _result_base(
            tool_name="read_file",
            decision=ALLOW,
            allowed=True,
            ok=ok,
            reason=policy_decision.reason,
            denial_reason="",
            latency_ms=latency_ms,
            error=error,
        ) | {
            "path": rel_path,
            "resolved_path": str(candidate_path),
            "content": _truncate_text(content, DEFAULT_TEXT_LIMIT),
            "bytes": len(content.encode("utf-8")),
        }
        return self._finalize(record)

    def write_file(self, path: str, content: str) -> dict[str, Any]:
        start = time.perf_counter()
        if not isinstance(content, str):
            latency_ms = (time.perf_counter() - start) * 1000.0
            return self._finalize(
                _result_base(
                    tool_name="write_file",
                    decision=DENY,
                    allowed=False,
                    ok=False,
                    reason="content must be a string",
                    denial_reason="content must be a string",
                    latency_ms=latency_ms,
                )
                | {"path": path, "resolved_path": "", "bytes_written": 0}
            )

        candidate_path, rel_path, path_error = _resolve_runtime_path(self.base_dir, path)
        if path_error is not None or rel_path is None or candidate_path is None:
            latency_ms = (time.perf_counter() - start) * 1000.0
            return self._finalize(
                _result_base(
                    tool_name="write_file",
                    decision=DENY,
                    allowed=False,
                    ok=False,
                    reason=path_error or "invalid path",
                    denial_reason=path_error or "invalid path",
                    latency_ms=latency_ms,
                )
                | {"path": path, "resolved_path": "", "bytes_written": 0}
            )

        policy_decision = _path_policy_decision(self.policy, rel_path)
        if not policy_decision.allowed:
            latency_ms = (time.perf_counter() - start) * 1000.0
            return self._finalize(
                _result_base(
                    tool_name="write_file",
                    decision=DENY,
                    allowed=False,
                    ok=False,
                    reason=policy_decision.reason,
                    denial_reason=policy_decision.reason,
                    latency_ms=latency_ms,
                )
                | {
                    "path": rel_path,
                    "resolved_path": str(candidate_path),
                    "bytes_written": 0,
                }
            )

        try:
            candidate_path.parent.mkdir(parents=True, exist_ok=True)
            candidate_path.write_text(content, encoding="utf-8")
            ok = True
            error = ""
            bytes_written = len(content.encode("utf-8"))
        except Exception as exc:  # pragma: no cover - exercised in live runs
            ok = False
            error = f"{type(exc).__name__}: {exc}"
            bytes_written = 0

        latency_ms = (time.perf_counter() - start) * 1000.0
        record = _result_base(
            tool_name="write_file",
            decision=ALLOW,
            allowed=True,
            ok=ok,
            reason=policy_decision.reason,
            denial_reason="",
            latency_ms=latency_ms,
            error=error,
        ) | {
            "path": rel_path,
            "resolved_path": str(candidate_path),
            "bytes_written": bytes_written,
        }
        return self._finalize(record)

    def http_get(self, url: str) -> dict[str, Any]:
        start = time.perf_counter()
        url_text = str(url).strip()
        parsed = urlparse(url_text)
        if parsed.scheme.lower() not in {"http", "https"}:
            latency_ms = (time.perf_counter() - start) * 1000.0
            return self._finalize(
                _result_base(
                    tool_name="http_get",
                    decision=DENY,
                    allowed=False,
                    ok=False,
                    reason="only http and https URLs are allowed",
                    denial_reason="only http and https URLs are allowed",
                    latency_ms=latency_ms,
                )
                | {"url": url_text, "status_code": None, "headers": {}, "body": ""}
            )
        if parsed.username or parsed.password:
            latency_ms = (time.perf_counter() - start) * 1000.0
            return self._finalize(
                _result_base(
                    tool_name="http_get",
                    decision=DENY,
                    allowed=False,
                    ok=False,
                    reason="URLs with embedded credentials are not allowed",
                    denial_reason="URLs with embedded credentials are not allowed",
                    latency_ms=latency_ms,
                )
                | {"url": url_text, "status_code": None, "headers": {}, "body": ""}
            )

        host = parsed.hostname or ""
        policy_decision = _domain_policy_decision(self.policy, host)
        if not policy_decision.allowed:
            latency_ms = (time.perf_counter() - start) * 1000.0
            return self._finalize(
                _result_base(
                    tool_name="http_get",
                    decision=DENY,
                    allowed=False,
                    ok=False,
                    reason=policy_decision.reason,
                    denial_reason=policy_decision.reason,
                    latency_ms=latency_ms,
                )
                | {"url": url_text, "status_code": None, "headers": {}, "body": ""}
            )

        try:
            response = self._session.get(
                url_text,
                timeout=self._timeout_s,
                allow_redirects=False,
            )
            headers = {
                key: value
                for key, value in response.headers.items()
                if key.lower() in {"content-type", "content-length", "date", "server", "location"}
            }
            body = _truncate_text(response.text, DEFAULT_BODY_LIMIT)
            ok = True
            error = ""
            status_code: int | None = int(response.status_code)
        except Exception as exc:  # pragma: no cover - exercised in live runs
            headers = {}
            body = ""
            ok = False
            error = f"{type(exc).__name__}: {exc}"
            status_code = None

        latency_ms = (time.perf_counter() - start) * 1000.0
        record = _result_base(
            tool_name="http_get",
            decision=ALLOW,
            allowed=True,
            ok=ok,
            reason=policy_decision.reason,
            denial_reason="",
            latency_ms=latency_ms,
            error=error,
        ) | {
            "url": url_text,
            "host": host,
            "status_code": status_code,
            "headers": headers,
            "body": body,
        }
        return self._finalize(record)


def build_tool_map(
    *,
    policy: PolicyConfig | None = None,
    policy_path: Path | str = DEFAULT_POLICY_PATH,
    base_dir: Path | str = DEFAULT_RUNTIME_ROOT,
    logger: ToolLogger | None = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> tuple[LiveEvalSentinelTools, dict[str, Callable[..., dict[str, Any]]]]:
    mediator = LiveEvalSentinelTools(
        policy=policy,
        policy_path=policy_path,
        base_dir=base_dir,
        logger=logger,
        timeout_s=timeout_s,
    )
    return mediator, {
        "read_file": mediator.read_file,
        "write_file": mediator.write_file,
        "http_get": mediator.http_get,
    }


def tool_schemas() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read a text file through Agent-Sentinel policy mediation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file to read.",
                        }
                    },
                    "required": ["path"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write a text file through Agent-Sentinel policy mediation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file to write.",
                        },
                        "content": {
                            "type": "string",
                            "description": "Text content to write.",
                        },
                    },
                    "required": ["path", "content"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "http_get",
                "description": "Fetch a URL through Agent-Sentinel policy mediation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "HTTP or HTTPS URL to fetch.",
                        }
                    },
                    "required": ["url"],
                    "additionalProperties": False,
                },
            },
        },
    ]
