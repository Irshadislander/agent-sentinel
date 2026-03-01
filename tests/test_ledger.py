import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_sentinel.forensics.ledger import FlightRecorder


def test_append_and_verify_success(tmp_path):
    log_path = tmp_path / "ledger.jsonl"
    recorder = FlightRecorder(str(log_path), run_id="run-123")

    recorder.append("agent_start", {"step": 1})
    recorder.append("agent_progress", {"step": 2})
    recorder.append("agent_finish", {"step": 3})

    assert recorder.verify() == (True, "ok")


def test_chain_break_detection(tmp_path):
    log_path = tmp_path / "ledger.jsonl"
    recorder = FlightRecorder(str(log_path), run_id="run-123")

    recorder.append("event", {"index": 0})
    recorder.append("event", {"index": 1})
    recorder.append("event", {"index": 2})

    lines = log_path.read_text(encoding="utf-8").splitlines()
    tampered = json.loads(lines[1])
    tampered["payload"]["index"] = 999
    lines[1] = json.dumps(tampered, sort_keys=True, separators=(",", ":"))
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    ok, _ = recorder.verify()
    assert ok is False


def test_redaction_masks_secrets(tmp_path):
    log_path = tmp_path / "ledger.jsonl"
    recorder = FlightRecorder(str(log_path), run_id="run-123")

    recorder.append("credentials_seen", {"api_token": "ABC123", "password": "P@ss"})

    content = log_path.read_text(encoding="utf-8")
    assert "ABC123" not in content
    assert "P@ss" not in content
    assert '"api_token":"***"' in content
    assert '"password":"***"' in content
