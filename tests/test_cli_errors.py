import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_sentinel.cli import main
from agent_sentinel.cli_exit_codes import DENIED, INVALID_POLICY, OK, UNKNOWN_CAPABILITY
from agent_sentinel.security.capabilities import FS_READ_PUBLIC, NET_HTTP_GET


def _write_policy(tmp_path: Path, data) -> str:
    p = tmp_path / "policy.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return str(p)


def test_cli_allowed(tmp_path, capsys):
    policy_path = _write_policy(tmp_path, {"allow": [FS_READ_PUBLIC]})
    rc = main(["--policy", policy_path, "--capability", FS_READ_PUBLIC])
    out = capsys.readouterr().out.strip()
    assert rc == OK
    assert out == "ALLOWED"


def test_cli_denied(tmp_path, capsys):
    policy_path = _write_policy(tmp_path, {"allow": [FS_READ_PUBLIC]})
    rc = main(["--policy", policy_path, "--capability", NET_HTTP_GET])
    err = capsys.readouterr().err
    assert rc == DENIED
    assert "PolicyViolationError" in err


def test_cli_unknown_capability(tmp_path, capsys):
    policy_path = _write_policy(tmp_path, {"allow": [FS_READ_PUBLIC]})
    rc = main(["--policy", policy_path, "--capability", "net.http.superget"])
    err = capsys.readouterr().err
    assert rc == UNKNOWN_CAPABILITY
    assert "UnknownCapabilityError" in err


def test_cli_invalid_policy(tmp_path, capsys):
    policy_path = _write_policy(tmp_path, {"allow": "not-a-list"})
    rc = main(["--policy", policy_path, "--capability", FS_READ_PUBLIC])
    err = capsys.readouterr().err
    assert rc == INVALID_POLICY
    assert "InvalidPolicyFormatError" in err
