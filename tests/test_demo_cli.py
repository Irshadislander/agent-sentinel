import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_sentinel.cli import run_demo
from agent_sentinel.forensics.verify import verify_log


def test_demo_produces_ledger(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    policy_path = tmp_path / "default.yaml"
    policy_path.write_text(
        "\n".join(
            [
                "default_deny: true",
                "granted_caps:",
                "  - fs.read.public",
                "  - fs.write.workspace",
                "  - net.http.get",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = run_demo(str(policy_path))
    ledger_path = Path(summary["ledger_path"])

    assert ledger_path.exists()
    assert ledger_path.read_text(encoding="utf-8").strip() != ""
    assert summary["allowed"] >= 1
    assert summary["denied"] >= 1


def test_demo_ledger_verification_passes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    policy_path = tmp_path / "default.yaml"
    policy_path.write_text(
        "\n".join(
            [
                "default_deny: true",
                "granted_caps:",
                "  - fs.read.public",
                "  - fs.write.workspace",
                "  - net.http.get",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = run_demo(str(policy_path))
    ok, reason = verify_log(summary["ledger_path"])
    assert (ok, reason) == (True, "ok")
