from __future__ import annotations

import json
from pathlib import Path

from agent_sentinel.benchmark.run_benchmark import BASELINES, run_matrix
from agent_sentinel.benchmark.run_benchmark import main as benchmark_main


def test_matrix_has_baseline_column_and_multiple_rows(tmp_path, monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    tasks_dir = repo_root / "configs" / "tasks"
    policy_path = repo_root / "configs" / "policies" / "default.yaml"
    output_dir = tmp_path / "bench-results"
    monkeypatch.chdir(tmp_path)

    matrix_json, matrix_csv, rows = run_matrix(
        tasks_dir=str(tasks_dir),
        policy_path=str(policy_path),
        output_dir=str(output_dir),
        baselines=["default", "no_trace"],
    )

    assert matrix_json.exists()
    assert matrix_csv.exists()
    assert rows
    assert len(rows) > 2
    assert {"baseline", "task_id", "decision", "exit_code", "duration_ms"}.issubset(
        set(rows[0].keys())
    )

    payload = json.loads(matrix_json.read_text(encoding="utf-8"))
    assert isinstance(payload.get("rows"), list)
    assert len(payload["rows"]) == len(rows)
    assert {item["baseline"] for item in payload["rows"]} == {"default", "no_trace"}


def test_baseline_no_trace_drops_trace_presence(tmp_path, monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    tasks_dir = repo_root / "configs" / "tasks"
    policy_path = repo_root / "configs" / "policies" / "default.yaml"
    output_dir = tmp_path / "bench-results"
    monkeypatch.chdir(tmp_path)

    _, _, rows = run_matrix(
        tasks_dir=str(tasks_dir),
        policy_path=str(policy_path),
        output_dir=str(output_dir),
        baselines=["default", "no_trace"],
    )

    default_rows = [row for row in rows if row["baseline"] == "default"]
    no_trace_rows = [row for row in rows if row["baseline"] == "no_trace"]
    assert default_rows and no_trace_rows
    assert all(bool(row["has_trace"]) for row in default_rows)
    assert all(not bool(row["has_trace"]) for row in no_trace_rows)


def test_baseline_no_policy_allows_blocked_tasks(tmp_path, monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    tasks_dir = repo_root / "configs" / "tasks"
    policy_path = repo_root / "configs" / "policies" / "default.yaml"
    output_dir = tmp_path / "bench-results"
    monkeypatch.chdir(tmp_path)

    _, _, rows = run_matrix(
        tasks_dir=str(tasks_dir),
        policy_path=str(policy_path),
        output_dir=str(output_dir),
        baselines=["default", "no_policy"],
    )

    default_malicious = [
        row for row in rows if row["baseline"] == "default" and row.get("category") == "malicious"
    ]
    no_policy_malicious = [
        row for row in rows if row["baseline"] == "no_policy" and row.get("category") == "malicious"
    ]
    assert default_malicious and no_policy_malicious
    assert any(row["decision"] == "deny" for row in default_malicious)
    assert all(row["decision"] == "allow" for row in no_policy_malicious)


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
            "--matrix-all-baselines",
        ]
    )

    assert rc == 0
    assert (output_dir / "matrix.json").exists()
    assert (output_dir / "matrix.csv").exists()
    payload = json.loads((output_dir / "matrix.json").read_text(encoding="utf-8"))
    baselines = {row["baseline"] for row in payload["rows"]}
    assert baselines == set(BASELINES)
    assert not (tmp_path / "public").exists()
    assert not (tmp_path / "workspace").exists()
