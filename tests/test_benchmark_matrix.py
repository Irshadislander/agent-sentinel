from __future__ import annotations

import json
from pathlib import Path

from agent_sentinel.benchmark.run_benchmark import BASELINES, run_matrix
from agent_sentinel.benchmark.run_benchmark import main as benchmark_main


def _uer(rows: list[dict[str, object]]) -> float:
    denied_expected = [row for row in rows if str(row.get("category", "")) != "benign"]
    if not denied_expected:
        return 0.0
    denied_but_executed = sum(1 for row in denied_expected if row.get("decision") == "allow")
    return denied_but_executed / len(denied_expected)


def _tcr(rows: list[dict[str, object]]) -> float:
    if not rows:
        return 0.0
    traced = sum(1 for row in rows if bool(row.get("has_trace")))
    return traced / len(rows)


def test_matrix_output_contains_all_baseline_keys(tmp_path, monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    tasks_dir = repo_root / "configs" / "tasks"
    policy_path = repo_root / "configs" / "policies" / "default.yaml"
    output_dir = tmp_path / "bench-results"
    monkeypatch.chdir(tmp_path)

    matrix_json, matrix_csv, rows = run_matrix(
        tasks_dir=str(tasks_dir),
        policy_path=str(policy_path),
        output_dir=str(output_dir),
        baselines=list(BASELINES),
    )

    assert matrix_json.exists()
    assert matrix_csv.exists()
    assert rows

    payload = json.loads(matrix_json.read_text(encoding="utf-8"))
    assert isinstance(payload.get("rows"), list)
    assert isinstance(payload.get("baselines"), dict)
    assert set(payload["baselines"].keys()) == set(BASELINES)
    assert {row["baseline"] for row in payload["rows"]} == set(BASELINES)


def test_matrix_has_expected_metric_differences_vs_default(tmp_path, monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    tasks_dir = repo_root / "configs" / "tasks"
    policy_path = repo_root / "configs" / "policies" / "default.yaml"
    output_dir = tmp_path / "bench-results"
    monkeypatch.chdir(tmp_path)

    _, _, rows = run_matrix(
        tasks_dir=str(tasks_dir),
        policy_path=str(policy_path),
        output_dir=str(output_dir),
        baselines=["default", "no_trace", "no_policy"],
    )

    default_rows = [row for row in rows if row["baseline"] == "default"]
    no_trace_rows = [row for row in rows if row["baseline"] == "no_trace"]
    no_policy_rows = [row for row in rows if row["baseline"] == "no_policy"]
    assert default_rows and no_trace_rows and no_policy_rows

    assert _tcr(no_trace_rows) < _tcr(default_rows)
    assert _uer(no_policy_rows) > _uer(default_rows)


def test_cli_matrix_baselines_option_selects_subset(tmp_path, monkeypatch) -> None:
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
            "--baselines",
            "default,no_trace",
        ]
    )

    assert rc == 0
    payload = json.loads((output_dir / "matrix.json").read_text(encoding="utf-8"))
    assert set(payload["baselines"].keys()) == {"default", "no_trace"}


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
    assert not (tmp_path / "public").exists()
    assert not (tmp_path / "workspace").exists()
