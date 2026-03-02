import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_sentinel.security.audit import to_json
from agent_sentinel.security.capabilities import FS_READ_PUBLIC, NET_HTTP_GET
from agent_sentinel.security.enforcer import enforce_request
from agent_sentinel.security.errors import PolicyViolationError


def test_allow_emits_allow_audit_event() -> None:
    policy = {"allow": [FS_READ_PUBLIC]}
    events = []

    enforce_request(FS_READ_PUBLIC, policy, audit_sink=events.append)

    assert len(events) == 1
    event = events[0]
    assert event.decision == "allow"
    assert event.capability == FS_READ_PUBLIC
    assert event.reason == "capability allowed by policy"


def test_deny_emits_deny_audit_event() -> None:
    policy = {"allow": [FS_READ_PUBLIC]}
    events = []

    with pytest.raises(PolicyViolationError):
        enforce_request(NET_HTTP_GET, policy, audit_sink=events.append)

    assert len(events) == 1
    event = events[0]
    assert event.decision == "deny"
    assert event.capability == NET_HTTP_GET
    assert event.reason == "PolicyViolationError"
    assert event.allowed_capabilities == [FS_READ_PUBLIC]


def test_audit_json_serialization_is_valid() -> None:
    policy = {"allow": [FS_READ_PUBLIC]}
    events = []

    enforce_request(FS_READ_PUBLIC, policy, audit_sink=events.append)
    payload = to_json(events[0])
    data = json.loads(payload)

    assert data["decision"] == "allow"
    assert data["capability"] == FS_READ_PUBLIC
    assert "timestamp_utc" in data
