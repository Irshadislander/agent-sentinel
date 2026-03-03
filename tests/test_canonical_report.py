from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _matrix_payload() -> dict[str, object]:
    rows = []
    baselines = ["default", "no_policy", "no_trace", "raw_errors", "no_plugin_isolation"]
    for baseline in baselines:
        rows.append(
            {
                "baseline": baseline,
                "scenario_id": "default",
                "task_id": f"{baseline}_benign",
                "category": "benign",
                "decision": "allow",
                "exit_code": 0,
                "duration_ms": 1.0,
                "has_trace": baseline != "no_trace",
                "reason_code": "RULE_ALLOW_MATCH",
                "error_kind": "none",
                "raw_error": "",
            }
        )
        rows.append(
            {
                "baseline": baseline,
                "scenario_id": "default",
                "task_id": f"{baseline}_blocked",
                "category": "policy_blocked",
                "decision": "allow" if baseline == "no_policy" else "deny",
                "exit_code": 0 if baseline == "no_policy" else 13,
                "duration_ms": 1.5,
                "has_trace": baseline != "no_trace",
                "reason_code": "DEFAULT_DENY_NO_MATCH" if baseline != "no_policy" else "",
                "error_kind": "raw_error" if baseline == "raw_errors" else "policy",
                "raw_error": "PermissionError: blocked" if baseline == "raw_errors" else "",
            }
        )
    return {"rows": rows}


def test_generate_canonical_report_outputs_required_files(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "generate_canonical_report.py"
    matrix_path = tmp_path / "artifacts" / "bench" / "matrix.json"
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_path.write_text(json.dumps(_matrix_payload()), encoding="utf-8")

    results_md = tmp_path / "paper" / "results_tables.md"
    perf_json = tmp_path / "artifacts" / "bench" / "policy_engine_bench.json"
    perf_md = tmp_path / "paper" / "PERF_DAYXX.md"
    robustness_json = tmp_path / "artifacts" / "bench" / "robustness_report.json"

    completed = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--matrix-input",
            str(matrix_path),
            "--results-output",
            str(results_md),
            "--policy-perf-json",
            str(perf_json),
            "--policy-perf-markdown",
            str(perf_md),
            "--robustness-output",
            str(robustness_json),
            "--perf-iterations",
            "10",
            "--perf-warmup",
            "1",
        ],
        text=True,
        capture_output=True,
    )
    assert completed.returncode == 0, completed.stderr

    assert results_md.exists()
    assert perf_json.exists()
    assert robustness_json.exists()
    assert perf_md.exists()

    markdown = results_md.read_text(encoding="utf-8")
    assert "## Results Summary Table" in markdown
    assert "Policy Decision Correctness" in markdown
    assert "Trace Completeness" in markdown
    assert "Reason-Code Correctness" in markdown
    assert "Stress Scaling Curve (n rules p95_ms)" in markdown
    assert "Robustness Pass Rate (attack suite)" in markdown

    expected_order = [
        "| no_policy |",
        "| no_trace |",
        "| raw_errors |",
        "| no_plugin_isolation |",
        "| default |",
    ]
    positions = [markdown.index(marker) for marker in expected_order]
    assert positions == sorted(positions)

    robustness = json.loads(robustness_json.read_text(encoding="utf-8"))
    assert "by_baseline" in robustness
    assert "denial_reason_counts" in robustness
    assert "denied_but_executed_total" in robustness
