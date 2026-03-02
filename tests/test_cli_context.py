import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_sentinel.cli import main
from agent_sentinel.cli_exit_codes import OK
from agent_sentinel.security.capabilities import FS_READ_PUBLIC


def _write_policy(tmp_path: Path, data) -> str:
    p = tmp_path / "policy.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return str(p)


def test_cli_audit_includes_request_context(tmp_path, capsys):
    policy_path = _write_policy(
        tmp_path,
        {"version": 1, "default": "deny", "allow": [FS_READ_PUBLIC]},
    )

    rc = main(
        [
            "--policy",
            policy_path,
            "--capability",
            FS_READ_PUBLIC,
            "--audit-json",
            "--request-id",
            "req123",
            "--correlation-id",
            "corr999",
            "--source",
            "cli",
        ]
    )

    err = capsys.readouterr().err.strip().splitlines()
    assert rc == OK

    json_line = next(line for line in err if line.startswith("{"))
    event = json.loads(json_line)

    assert event["request_id"] == "req123"
    assert event["correlation_id"] == "corr999"
    assert event["source"] == "cli"
    assert event["capability"] == FS_READ_PUBLIC
