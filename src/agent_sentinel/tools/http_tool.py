import json
from urllib.request import Request, urlopen


def http_get(url: str, timeout_s: int = 10) -> dict:
    request = Request(url=url, method="GET")
    with urlopen(request, timeout=timeout_s) as response:
        body = response.read().decode("utf-8", errors="replace")
        return {
            "url": url,
            "status": int(response.status),
            "body_snippet": body[:300],
        }


def http_post(url: str, json_body: dict, timeout_s: int = 10) -> dict:
    payload = json.dumps(json_body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    request = Request(
        url=url,
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=timeout_s) as response:
        body = response.read().decode("utf-8", errors="replace")
        return {
            "url": url,
            "status": int(response.status),
            "body_snippet": body[:300],
        }
