from __future__ import annotations

import json
from pathlib import Path

from agent_sentinel.benchmark.policy_engine_perf import (
    run_policy_engine_benchmark,
    write_policy_engine_benchmark_outputs,
)


def test_run_policy_engine_benchmark_has_required_cases() -> None:
    payload = run_policy_engine_benchmark(iterations=25, warmup=5)
    assert payload["benchmark"] == "policy_engine_perf"

    cases = payload["cases"]
    assert isinstance(cases, list)
    case_ids = {str(case["case_id"]) for case in cases}
    assert case_ids == {
        "allow_match_early",
        "deny_match_early",
        "no_match_default_deny",
        "invalid_policy",
        "missing_policy",
    }

    for case in cases:
        assert float(case["mean_ms"]) >= 0.0
        assert float(case["p50_ms"]) >= 0.0
        assert float(case["p95_ms"]) >= 0.0
        assert float(case["p99_ms"]) >= 0.0
        assert float(case["trace_len_mean"]) >= 0.0

    scaling_curve = payload["scaling_curve"]
    assert isinstance(scaling_curve, list)
    assert scaling_curve
    for point in scaling_curve:
        assert int(point["n_rules"]) > 0
        assert float(point["p95_ms"]) >= 0.0
        assert float(point["trace_len_mean"]) >= 0.0


def test_write_policy_engine_benchmark_outputs(tmp_path: Path) -> None:
    payload = run_policy_engine_benchmark(iterations=10, warmup=2)
    json_path = tmp_path / "artifacts" / "bench" / "policy_engine_bench.json"
    markdown_path = tmp_path / "paper" / "PERF_DAYXX.md"
    written_json, written_markdown = write_policy_engine_benchmark_outputs(
        payload,
        json_path=json_path,
        markdown_path=markdown_path,
    )

    assert written_json.exists()
    assert written_markdown.exists()

    parsed = json.loads(written_json.read_text(encoding="utf-8"))
    assert parsed["benchmark"] == "policy_engine_perf"
    markdown = written_markdown.read_text(encoding="utf-8")
    assert "# Policy Engine Performance" in markdown
    assert "| case | decision | reason_code | rule_id |" in markdown
    assert "## Stress Scaling Curve (n rules)" in markdown
