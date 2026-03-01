import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_sentinel.forensics.ledger import FlightRecorder
from agent_sentinel.security.capabilities import NET_HTTP_GET, CapabilitySet
from agent_sentinel.security.tool_gateway import ToolGateway


def _recorder(tmp_path: Path) -> FlightRecorder:
    return FlightRecorder(str(tmp_path / "forensics" / "http-policy.jsonl"), run_id="run-http")


def _http_request_stub(
    method: str,
    url: str,
    *,
    headers=None,
    params=None,
    data=None,
    json=None,
    timeout=10,
) -> dict:
    del headers, params, data, json, timeout
    return {"status_code": 200, "headers": {}, "text": f"{method}:{url}"}


def test_tool_gateway_denies_non_allowlisted_http_request(tmp_path):
    gateway = ToolGateway(
        policy={"allowlist_domains": ["api.github.com"], "capabilities": {"net.http.post": False}},
        recorder=_recorder(tmp_path),
        caps=CapabilitySet({NET_HTTP_GET}),
        tools={"http_request": _http_request_stub},
    )

    result = gateway.execute("http_request", {"method": "GET", "url": "https://evil.com"})
    assert result["ok"] is False


def test_tool_gateway_denies_post_without_capability(tmp_path):
    gateway = ToolGateway(
        policy={"allowlist_domains": ["api.github.com"], "capabilities": {"net.http.post": False}},
        recorder=_recorder(tmp_path),
        caps=CapabilitySet({NET_HTTP_GET}),
        tools={"http_request": _http_request_stub},
    )

    result = gateway.execute(
        "http_request",
        {
            "method": "POST",
            "url": "https://api.github.com/repos/openai/openai-python/issues",
            "json": {"title": "should be blocked"},
        },
    )
    assert result["ok"] is False
