from __future__ import annotations

import json
from pathlib import Path

from agent_sentinel.benchmark.report import generate_report


def test_report_includes_robustness_reason_code_sections(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    input_path = Path("bench/results/latest.json")
    matrix_path = Path("bench/results/matrix.json")
    output_path = Path("docs/bench_report.md")
    input_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    input_payload = {
        "benchmark_id": "bench_robustness",
        "tasks_total": 2,
        "baseline": {"metrics": {}, "results": []},
        "secured": {"metrics": {}, "results": []},
    }
    matrix_payload = {
        "rows": [
            {
                "baseline": "default",
                "task_id": "policy_blocked_task",
                "category": "policy_blocked",
                "decision": "deny",
                "exit_code": 13,
                "duration_ms": 0.2,
                "has_trace": True,
                "reason_code": "DEFAULT_DENY_NO_MATCH",
                "error_kind": "policy",
                "raw_error": "",
            },
            {
                "baseline": "default",
                "task_id": "malformed_payload_task",
                "category": "malformed_payload",
                "decision": "deny",
                "exit_code": 13,
                "duration_ms": 0.3,
                "has_trace": True,
                "reason_code": "POLICY_INVALID",
                "error_kind": "invalid",
                "raw_error": "",
            },
        ]
    }
    input_path.write_text(json.dumps(input_payload), encoding="utf-8")
    matrix_path.write_text(json.dumps(matrix_payload), encoding="utf-8")

    generate_report(
        input_path=input_path,
        output_path=output_path,
        matrix_input_path=matrix_path,
        generated_at="2026-03-03T00:00:00Z",
        git_sha="deadbeef",
    )

    content = output_path.read_text(encoding="utf-8")
    assert "## Robustness: Denial Reason Codes" in content
    assert "## Robustness: Top Reason Codes by Category" in content
    assert "Denied-but-executed (critical): `0`" in content
    assert "| DEFAULT_DENY_NO_MATCH | 1 |" in content
    assert "| POLICY_INVALID | 1 |" in content
