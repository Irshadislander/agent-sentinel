import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_sentinel.security.validators import (
    validate_fs_read,
    validate_http_request,
)


def test_validate_http_request_blocks_non_allowlisted() -> None:
    result = validate_http_request(
        method="GET",
        url="https://evil.com",
        allowlist_domains=["api.github.com"],
        allow_post=False,
    )
    assert result.allowed is False


def test_validate_http_request_blocks_post_by_default() -> None:
    result = validate_http_request(
        method="POST",
        url="https://api.github.com/events",
        allowlist_domains=["api.github.com"],
        allow_post=False,
    )
    assert result.allowed is False


def test_validate_http_request_allows_allowlisted_get() -> None:
    result = validate_http_request(
        method="GET",
        url="https://api.github.com/repos/openai/openai-python",
        allowlist_domains=["api.github.com"],
        allow_post=False,
    )
    assert result.allowed is True


def test_validate_fs_read_blocks_private_without_capability(tmp_path) -> None:
    base_dir = tmp_path
    result = validate_fs_read("private/secret.txt", base_dir=base_dir, allow_private=False)
    assert result.allowed is False

    allowed = validate_fs_read("private/secret.txt", base_dir=base_dir, allow_private=True)
    assert allowed.allowed is True
