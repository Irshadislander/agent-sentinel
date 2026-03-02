import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_sentinel.security.capabilities import (  # noqa: E402
    ALL_CAPABILITIES,
    FS_READ_PUBLIC,
    NET_HTTP_POST,
    get_capability,
    is_known,
)
from agent_sentinel.security.capability_model import CapabilityCategory, RiskLevel  # noqa: E402


def test_registry_knows_builtin_capabilities():
    assert is_known(FS_READ_PUBLIC)
    assert is_known(NET_HTTP_POST)


def test_all_capabilities_contains_expected():
    assert FS_READ_PUBLIC in ALL_CAPABILITIES
    assert NET_HTTP_POST in ALL_CAPABILITIES


def test_get_capability_returns_metadata():
    cap = get_capability(NET_HTTP_POST)
    assert cap is not None
    assert cap.name == NET_HTTP_POST
    assert cap.category == CapabilityCategory.NETWORK
    assert cap.risk == RiskLevel.HIGH
