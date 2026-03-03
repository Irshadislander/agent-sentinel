from __future__ import annotations

import json
from pathlib import Path

from agent_sentinel.benchmark.run_benchmark import main as benchmark_main
from agent_sentinel.benchmark.synthetic import generate_synthetic_tasks


def _read_synthetic_payloads(directory: Path) -> dict[str, dict]:
    payloads: dict[str, dict] = {}
    for path in sorted(directory.glob("synthetic_*.json")):
        payloads[path.name] = json.loads(path.read_text(encoding="utf-8"))
    return payloads


def test_generate_synthetic_tasks_is_deterministic(tmp_path: Path) -> None:
    out_a = tmp_path / "a"
    out_b = tmp_path / "b"
    mix = {
        "benign": 0.6,
        "policy_blocked": 0.2,
        "malformed_payload": 0.1,
        "trace_required": 0.05,
        "plugin_violation": 0.05,
    }

    paths_a = generate_synthetic_tasks(str(out_a), n=20, seed=123, mix=mix)
    paths_b = generate_synthetic_tasks(str(out_b), n=20, seed=123, mix=mix)

    assert [Path(path).name for path in paths_a] == [Path(path).name for path in paths_b]
    assert _read_synthetic_payloads(out_a) == _read_synthetic_payloads(out_b)


def test_cli_synthetic_generates_expected_task_count(tmp_path, monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    policy_path = repo_root / "configs" / "policies" / "default.yaml"
    output_dir = tmp_path / "bench-results"
    synthetic_dir = tmp_path / "synth"
    monkeypatch.chdir(tmp_path)

    rc = benchmark_main(
        [
            "--policy",
            str(policy_path),
            "--output-dir",
            str(output_dir),
            "--synthetic",
            "12",
            "--synthetic-seed",
            "7",
            "--synthetic-out-dir",
            str(synthetic_dir),
        ]
    )

    assert rc == 0
    assert len(list((synthetic_dir / "scale_n12").glob("synthetic_*.json"))) == 12


def test_matrix_rows_include_scenario_id(tmp_path, monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    tasks_dir = repo_root / "configs" / "tasks"
    policy_path = repo_root / "configs" / "policies" / "default.yaml"
    output_dir = tmp_path / "bench-results"
    synthetic_dir = tmp_path / "synth"
    monkeypatch.chdir(tmp_path)

    rc = benchmark_main(
        [
            "--policy",
            str(policy_path),
            "--tasks-dir",
            str(tasks_dir),
            "--output-dir",
            str(output_dir),
            "--synthetic-out-dir",
            str(synthetic_dir),
            "--matrix",
            "--baselines",
            "default,no_trace",
            "--scenarios",
            "scale_n5,stress_m0.10_p0.05,sens_strict=high_trace=0.5_allow=1",
        ]
    )

    assert rc == 0
    payload = json.loads((output_dir / "matrix.json").read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    assert rows
    scenario_ids = {row["scenario_id"] for row in rows}
    assert {"scale_n5", "stress_m0.10_p0.05", "sens_strict=high_trace=0.5_allow=1"} <= scenario_ids
