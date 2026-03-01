import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_sentinel.forensics.ledger import FlightRecorder
from agent_sentinel.security.capabilities import (
    FS_WRITE_WORKSPACE,
    NET_EXTERNAL,
    NET_HTTP_GET,
    CapabilitySet,
)
from agent_sentinel.security.tool_gateway import ToolGateway
from agent_sentinel.tools.fs_tool import write_text


def _recorder(tmp_path: Path) -> FlightRecorder:
    return FlightRecorder(str(tmp_path / "forensics" / "run.jsonl"), run_id="run-1")


def _http_get_stub(url: str, timeout_s: int = 10) -> dict:
    return {"url": url, "status": 200, "body_snippet": f"ok:{timeout_s}"}


def test_external_http_get_denied_by_default_without_caps(tmp_path):
    gateway = ToolGateway(
        policy={},
        recorder=_recorder(tmp_path),
        caps=CapabilitySet(set()),
        tools={"http_get": _http_get_stub},
    )

    with pytest.raises(PermissionError):
        gateway.execute("http_get", {"url": "https://example.com"})


def test_allow_http_get_with_external_and_http_get_caps(tmp_path):
    caps = CapabilitySet({NET_EXTERNAL, NET_HTTP_GET})
    gateway = ToolGateway(
        policy={},
        recorder=_recorder(tmp_path),
        caps=caps,
        tools={"http_get": _http_get_stub},
    )

    result = gateway.execute("http_get", {"url": "https://example.com", "timeout_s": 3})
    assert result["status"] == 200
    assert result["url"] == "https://example.com"


def test_deny_write_outside_workspace(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    caps = CapabilitySet({FS_WRITE_WORKSPACE})
    gateway = ToolGateway(
        policy={},
        recorder=_recorder(tmp_path),
        caps=caps,
        tools={"write_text": write_text},
    )

    with pytest.raises(PermissionError):
        gateway.execute("write_text", {"path": "private/blocked.txt", "text": "blocked"})


def test_allow_write_inside_workspace_with_cap(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    caps = CapabilitySet({FS_WRITE_WORKSPACE})
    gateway = ToolGateway(
        policy={},
        recorder=_recorder(tmp_path),
        caps=caps,
        tools={"write_text": write_text},
    )

    result = gateway.execute("write_text", {"path": "workspace/allowed.txt", "text": "hello"})
    assert result["path"] == "workspace/allowed.txt"
    assert result["bytes"] == 5
    assert (tmp_path / "workspace" / "allowed.txt").read_text(encoding="utf-8") == "hello"
