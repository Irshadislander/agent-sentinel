from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path


def test_benchmark_harness_writes_json_and_csv(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env.setdefault("PYTHONHASHSEED", "0")
    src_path = repo_root / "src"
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        str(src_path) if not existing_pythonpath else f"{src_path}:{existing_pythonpath}"
    )

    result = subprocess.run(
        [
            sys.executable,
            "bench/run_bench.py",
            "--iterations",
            "2",
            "--output-dir",
            str(tmp_path),
        ],
        cwd=repo_root,
        env=env,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr

    json_path = tmp_path / "latest.json"
    csv_path = tmp_path / "latest.csv"
    assert json_path.exists()
    assert csv_path.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["iterations"] == 2
    assert payload["schema_version"] == "1"
    assert "metrics" in payload

    required_metrics = {
        "cli_cold_start_ms",
        "cli_warm_start_ms",
        "registry_plugin_discovery_ms",
        "payload_validation_ms",
        "trace_observability_overhead_ms",
        "capability_execution_e2e_ms",
    }
    assert required_metrics.issubset(set(payload["metrics"]))

    for metric_name in sorted(required_metrics):
        metric = payload["metrics"][metric_name]
        assert "samples" in metric
        assert "stats" in metric
        stats = metric["stats"]
        for key in ("mean", "p50", "p95", "min", "max", "std"):
            assert key in stats

    with csv_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    assert rows
    header_fields = set(rows[0].keys())
    assert {"metric", "iterations", "mean", "p50", "p95", "min", "max", "std"}.issubset(
        header_fields
    )
