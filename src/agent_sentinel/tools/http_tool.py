from __future__ import annotations

from typing import Any
from urllib.parse import urlencode, urlparse, urlunparse

import requests

_HEADER_ALLOWLIST = ("content-type", "content-length", "date", "server", "location")


def _apply_params(url: str, params: dict[str, Any] | None) -> str:
    if not params:
        return url
    parsed = urlparse(url)
    query = urlencode(params, doseq=True)
    return urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path, parsed.params, query, parsed.fragment)
    )


def _header_subset(headers: Any) -> dict[str, str]:
    subset: dict[str, str] = {}
    for key, value in headers.items():
        if key.lower() in _HEADER_ALLOWLIST:
            subset[key] = value
    return subset


def http_request(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    data: Any = None,
    json: Any = None,
    timeout: int = 10,
    allow_redirects: bool = False,
) -> dict:
    target = _apply_params(url, params)
    response = requests.request(
        method=method.upper(),
        url=target,
        headers=headers,
        data=data,
        json=json,
        timeout=timeout,
        allow_redirects=allow_redirects,
    )
    return {
        "status_code": response.status_code,
        "headers": _header_subset(response.headers),
        "text": response.text[:2000],
    }


def http_get(url: str, timeout_s: int = 10) -> dict:
    result = http_request("GET", url, timeout=timeout_s)
    return {
        "url": url,
        "status": int(result["status_code"]),
        "body_snippet": str(result["text"])[:300],
    }


def http_post(url: str, json_body: dict, timeout_s: int = 10) -> dict:
    result = http_request("POST", url, json=json_body, timeout=timeout_s)
    return {
        "url": url,
        "status": int(result["status_code"]),
        "body_snippet": str(result["text"])[:300],
    }
