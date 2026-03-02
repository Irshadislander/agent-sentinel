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


def test_cli_benchmark_outputs_metrics(tmp_path, capsys):
    policy_path = _write_policy(tmp_path, {"allow": [FS_READ_PUBLIC]})

    rc = main(
        [
            "--policy",
            policy_path,
            "--capability",
            FS_READ_PUBLIC,
            "--benchmark",
            "--iterations",
            "50",
            "--warmup",
            "5",
        ]
    )

    out = capsys.readouterr().out
    assert rc == OK
    assert "Policy enforcement benchmark" in out
    assert "Iterations: 50" in out


def test_cli_benchmark_json_mode(tmp_path, capsys):
    policy_path = _write_policy(tmp_path, {"allow": [FS_READ_PUBLIC]})

    rc = main(
        [
            "--policy",
            policy_path,
            "--capability",
            FS_READ_PUBLIC,
            "--benchmark",
            "--iterations",
            "10",
            "--warmup",
            "0",
            "--json",
        ]
    )

    out = capsys.readouterr().out.strip()
    assert rc == OK
    data = json.loads(out)
    assert data["iterations"] == 10
    assert "avg_ms" in data
    assert "min_ms" in data
    assert "max_ms" in data
