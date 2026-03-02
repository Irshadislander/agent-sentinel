import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_sentinel.security.capabilities import (  # noqa: E402
    FS_READ_PUBLIC,
    FS_WRITE_WORKSPACE,
    NET_EXTERNAL,
    NET_HTTP_GET,
    NET_INTERNAL,
)
from agent_sentinel.security.policy_engine import (  # noqa: E402
    ALLOW,
    ALLOW_WITH_REDACTION,
    DENY,
    REQUIRE_APPROVAL,
    PolicyEngine,
)


def test_http_get_localhost_requires_internal_capability() -> None:
    engine = PolicyEngine(policy={})

    denied = engine.decide(
        tool_name="http_get",
        args={"url": "http://localhost:8000/health"},
        caps={NET_HTTP_GET},
    )
    assert denied.verdict == DENY
    assert "net.internal" in denied.reason

    allowed = engine.decide(
        tool_name="http_get",
        args={"url": "http://localhost:8000/health"},
        caps={NET_HTTP_GET, NET_INTERNAL},
    )
    assert allowed.verdict == ALLOW


def test_http_get_external_sensitive_payload_requires_approval() -> None:
    engine = PolicyEngine(policy={})

    decision = engine.decide(
        tool_name="http_get",
        args={"url": "https://example.com/api", "token": "abc123"},
        caps={NET_HTTP_GET, NET_EXTERNAL},
    )
    assert decision.verdict == REQUIRE_APPROVAL
    assert "sensitive payload" in decision.reason


def test_http_get_non_http_scheme_treated_as_external() -> None:
    engine = PolicyEngine(policy={})

    denied = engine.decide(
        tool_name="http_get",
        args={"url": "ftp://internal.local/file.txt"},
        caps={NET_HTTP_GET},
    )
    assert denied.verdict == DENY
    assert "net.external" in denied.reason


def test_fs_read_rejects_path_traversal_even_with_public_cap() -> None:
    engine = PolicyEngine(policy={})

    decision = engine.decide(
        tool_name="read_text",
        args={"path": "../public/readme.md"},
        caps={FS_READ_PUBLIC},
    )
    assert decision.verdict == DENY
    assert "invalid path" in decision.reason


def test_http_get_internal_domain_from_policy_requires_internal_capability() -> None:
    engine = PolicyEngine(policy={"internal_domains": ["corp.example.com"]})

    denied = engine.decide(
        tool_name="http_get",
        args={"url": "https://api.corp.example.com/v1/health"},
        caps={NET_HTTP_GET},
    )
    assert denied.verdict == DENY
    assert "net.internal" in denied.reason

    allowed = engine.decide(
        tool_name="http_get",
        args={"url": "https://api.corp.example.com/v1/health"},
        caps={NET_HTTP_GET, NET_INTERNAL},
    )
    assert allowed.verdict == ALLOW


def test_fs_read_allows_with_redaction_when_auto_redact_enabled() -> None:
    engine = PolicyEngine(policy={"auto_redact_args": True})

    decision = engine.decide(
        tool_name="read_text",
        args={"path": "public/readme.md", "auth": {"api_token": "super-secret-value"}},
        caps={FS_READ_PUBLIC},
    )
    assert decision.verdict == ALLOW_WITH_REDACTION
    assert decision.redactions == {"auth.api_token": "***"}


def test_fs_write_absolute_path_is_invalid_even_with_workspace_capability() -> None:
    engine = PolicyEngine(policy={})

    decision = engine.decide(
        tool_name="write_text",
        args={"path": "/workspace/report.txt", "text": "blocked"},
        caps={FS_WRITE_WORKSPACE},
    )
    assert decision.verdict == DENY
    assert "invalid path" in decision.reason
