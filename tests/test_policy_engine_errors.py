import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_sentinel.security.capabilities import FS_READ_PUBLIC, NET_HTTP_GET
from agent_sentinel.security.errors import (
    InvalidPolicyFormatError,
    PolicyViolationError,
    UnknownCapabilityError,
)
from agent_sentinel.security.policy_engine import enforce


def test_unknown_capability_raises():
    policy = {"allow": [FS_READ_PUBLIC]}
    with pytest.raises(UnknownCapabilityError):
        enforce("fs.read.nonexistent", policy)


def test_invalid_policy_missing_allow():
    with pytest.raises(InvalidPolicyFormatError):
        enforce(FS_READ_PUBLIC, {})


def test_invalid_policy_allow_not_list():
    with pytest.raises(InvalidPolicyFormatError):
        enforce(FS_READ_PUBLIC, {"allow": "not-a-list"})


def test_invalid_policy_allow_contains_non_str():
    with pytest.raises(InvalidPolicyFormatError):
        enforce(FS_READ_PUBLIC, {"allow": [FS_READ_PUBLIC, 123]})


def test_policy_violation_error_fields_are_stable():
    policy = {"allow": [FS_READ_PUBLIC]}
    with pytest.raises(PolicyViolationError) as exc:
        enforce(NET_HTTP_GET, policy)

    err = exc.value
    assert err.requested_capability == NET_HTTP_GET
    assert FS_READ_PUBLIC in err.allowed_capabilities
