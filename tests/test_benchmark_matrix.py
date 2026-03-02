from __future__ import annotations

import json
from pathlib import Path

from agent_sentinel.benchmark.run_benchmark import main as benchmark_main
from agent_sentinel.benchmark.run_benchmark import run_matrix


def test_matrix_mode_runs_and_writes_outputs(tmp_path, monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    tasks_dir = repo_root / "configs" / "tasks"
    policy_path = repo_root / "configs" / "policies" / "default.yaml"
    output_dir = tmp_path / "bench-results"
    monkeypatch.chdir(tmp_path)

    matrix_json, matrix_csv, runs = run_matrix(
        tasks_dir=str(tasks_dir),
        policy_path=str(policy_path),
        output_dir=str(output_dir),
    )

    assert matrix_json.exists()
    assert matrix_csv.exists()
    assert len(runs) == 8
    for row in runs:
        assert "mode_label" in row
        assert "avg_runtime_ms" in row
        assert "exit_code_histogram" in row
        assert "failure_count" in row
        assert "trace_event_count" in row

    payload = json.loads(matrix_json.read_text(encoding="utf-8"))
    assert isinstance(payload.get("runs"), list)
    assert len(payload["runs"]) == 8


def test_matrix_mode_does_not_write_public_or_workspace(tmp_path, monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    tasks_dir = repo_root / "configs" / "tasks"
    policy_path = repo_root / "configs" / "policies" / "default.yaml"
    output_dir = tmp_path / "bench-results"
    monkeypatch.chdir(tmp_path)

    rc = benchmark_main(
        [
            "--tasks-dir",
            str(tasks_dir),
            "--policy",
            str(policy_path),
            "--output-dir",
            str(output_dir),
            "--matrix",
        ]
    )

    assert rc == 0
    assert (output_dir / "matrix.json").exists()
    assert (output_dir / "matrix.csv").exists()
    assert not (tmp_path / "public").exists()
    assert not (tmp_path / "workspace").exists()
