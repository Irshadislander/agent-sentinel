import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_sentinel.security.capabilities import FS_READ_PUBLIC, NET_HTTP_GET
from agent_sentinel.security.errors import PolicyViolationError, UnknownCapabilityError
from agent_sentinel.security.sim_harness import AgentRuntime, ToolCall


def fake_read_public() -> str:
    return "ok"


def fake_http_get() -> str:
    return "net-ok"


def test_runtime_allows_registered_allowed_tool():
    policy = {"allow": [FS_READ_PUBLIC]}
    rt = AgentRuntime(policy)

    rt.register_tool(
        ToolCall(tool_name="read_public", capability=FS_READ_PUBLIC, fn=fake_read_public)
    )

    out = rt.call("read_public")
    assert out == "ok"


def test_runtime_denies_tool_when_policy_blocks():
    policy = {"allow": [FS_READ_PUBLIC]}
    rt = AgentRuntime(policy)

    rt.register_tool(ToolCall(tool_name="http_get", capability=NET_HTTP_GET, fn=fake_http_get))

    with pytest.raises(PolicyViolationError) as exc:
        rt.call("http_get")

    assert exc.value.requested_capability == NET_HTTP_GET


def test_runtime_unknown_capability_blocks():
    policy = {"allow": [FS_READ_PUBLIC]}
    rt = AgentRuntime(policy)

    rt.register_tool(
        ToolCall(tool_name="mystery", capability="net.http.superget", fn=fake_http_get)
    )

    with pytest.raises(UnknownCapabilityError) as exc:
        rt.call("mystery")

    assert exc.value.requested_capability == "net.http.superget"


def test_runtime_unregistered_tool_name_raises_keyerror():
    policy = {"allow": [FS_READ_PUBLIC]}
    rt = AgentRuntime(policy)

    with pytest.raises(KeyError):
        rt.call("not_registered")
