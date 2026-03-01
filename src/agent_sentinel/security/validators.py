from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse

_PRIVATE_PATH_PATTERNS = (
    re.compile(r"(^|/)\.env($|[./])", re.IGNORECASE),
    re.compile(r"(^|/)private($|/)", re.IGNORECASE),
    re.compile(
        r"(^|/).*(id_rsa|id_dsa|\.pem|\.p12|\.pfx|\.key|certificate|cert)($|[./])", re.IGNORECASE
    ),
)
_KEY_LIKE_VALUE_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ASIA[0-9A-Z]{16}"),
    re.compile(r"(?i)(secret|token|password|api[_-]?key)[=:]\s*[A-Za-z0-9_\-]{8,}"),
    re.compile(r"^[A-Za-z0-9_\-]{24,}$"),
)
_EXFIL_PATTERNS = (
    re.compile(r"BEGIN PRIVATE KEY"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"[A-Za-z0-9+/]{200,}={0,2}"),
)
_SENSITIVE_KEY_NAMES = ("key", "token", "secret", "password", "credential", "passwd")
_UNSAFE_HTTP_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


@dataclass(slots=True)
class ValidationResult:
    allowed: bool
    reason: str = ""
    redacted_args: dict | None = None


def parse_url(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    return parsed.scheme.lower(), (parsed.hostname or "").lower()


def _normalize_relative_path(path: str) -> PurePosixPath:
    normalized = path.replace("\\", "/")
    return PurePosixPath(normalized)


def _looks_like_secret_value(value: str) -> bool:
    text = value.strip()
    if len(text) < 8:
        return False
    return any(pattern.search(text) for pattern in _KEY_LIKE_VALUE_PATTERNS)


def _allowlisted_host(host: str, allowlist_domains: list[str]) -> bool:
    lowered = host.lower()
    for domain in allowlist_domains:
        allowed = domain.lower().lstrip(".")
        if lowered == allowed or lowered.endswith(f".{allowed}"):
            return True
    return False


def is_private_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return any(pattern.search(normalized) for pattern in _PRIVATE_PATH_PATTERNS)


def validate_fs_read(path: str, base_dir: str | Path, allow_private: bool) -> ValidationResult:
    if not isinstance(path, str) or not path:
        return ValidationResult(False, "invalid fs path")

    posix_path = _normalize_relative_path(path)
    if posix_path.is_absolute():
        return ValidationResult(False, "absolute paths are not allowed")
    if any(part == ".." for part in posix_path.parts):
        return ValidationResult(False, "path traversal is not allowed")

    root = Path(base_dir).resolve()
    candidate = (root / posix_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return ValidationResult(False, "path escapes base_dir")

    if is_private_path(path) and not allow_private:
        return ValidationResult(False, "private path access denied")
    return ValidationResult(True, "ok")


def validate_http_request(
    method: str,
    url: str,
    allowlist_domains: list[str],
    allow_post: bool,
) -> ValidationResult:
    if not isinstance(method, str) or not method:
        return ValidationResult(False, "invalid http method")
    if not isinstance(url, str) or not url:
        return ValidationResult(False, "invalid http url")

    normalized_method = method.upper()
    scheme, host = parse_url(url)

    if scheme not in {"http", "https"}:
        return ValidationResult(False, "only http/https schemes are allowed")
    if not host:
        return ValidationResult(False, "missing destination host")
    if not _allowlisted_host(host, allowlist_domains):
        return ValidationResult(False, f"host not allowlisted: {host}")

    if normalized_method in _UNSAFE_HTTP_METHODS and not allow_post:
        return ValidationResult(False, f"{normalized_method} not allowed by policy")

    return ValidationResult(True, "ok")


def detect_exfil(text_or_bytes: str | bytes) -> bool:
    if isinstance(text_or_bytes, bytes):
        text = text_or_bytes.decode("utf-8", errors="ignore")
    else:
        text = text_or_bytes
    return any(pattern.search(text) for pattern in _EXFIL_PATTERNS)


def redact_secrets(obj: Any) -> Any:
    if isinstance(obj, dict):
        redacted: dict[str, Any] = {}
        for key, value in obj.items():
            key_text = str(key)
            if any(marker in key_text.lower() for marker in _SENSITIVE_KEY_NAMES):
                redacted[key_text] = "<REDACTED>"
                continue
            redacted[key_text] = redact_secrets(value)
        return redacted

    if isinstance(obj, list):
        return [redact_secrets(item) for item in obj]

    if isinstance(obj, tuple):
        return [redact_secrets(item) for item in obj]

    if isinstance(obj, bytes):
        return "<REDACTED>" if detect_exfil(obj) else obj.decode("utf-8", errors="replace")

    if isinstance(obj, str):
        return "<REDACTED>" if _looks_like_secret_value(obj) or detect_exfil(obj) else obj

    return obj
