from __future__ import annotations

import json

from agent_sentinel.benchmark.run_benchmark import main as benchmark_main


def test_matrix_policy_engine_perf_scenario_writes_artifacts(tmp_path, monkeypatch) -> None:
    output_dir = tmp_path / "bench-results"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AGENT_SENTINEL_POLICY_PERF_ITERATIONS", "30")
    monkeypatch.setenv("AGENT_SENTINEL_POLICY_PERF_WARMUP", "3")

    rc = benchmark_main(
        [
            "--matrix",
            "--scenarios",
            "policy_engine_perf",
            "--baselines",
            "default,no_trace",
            "--output-dir",
            str(output_dir),
        ]
    )

    assert rc == 0
    matrix_json = output_dir / "matrix.json"
    matrix_csv = output_dir / "matrix.csv"
    assert matrix_json.exists()
    assert matrix_csv.exists()

    payload = json.loads(matrix_json.read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    assert rows
    assert {row["scenario_id"] for row in rows} == {"policy_engine_perf"}
    assert {row["baseline"] for row in rows} == {"default", "no_trace"}
    assert {"allow_match_early", "missing_policy"} <= {row["task_id"] for row in rows}

    perf_dir = output_dir / "policy_engine_perf"
    assert (perf_dir / "default.json").exists()
    assert (perf_dir / "default.md").exists()
    assert (perf_dir / "no_trace.json").exists()
    assert (perf_dir / "no_trace.md").exists()
