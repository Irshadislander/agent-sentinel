from __future__ import annotations

import argparse
import csv
import itertools
import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agent_sentinel.benchmark.runner import (
    DEFAULT_POLICY_PATH,
    DEFAULT_TASKS_DIR,
)
from agent_sentinel.benchmark.runner import (
    run_benchmark as execute_benchmark,
)
from agent_sentinel.cli_exit_codes import DENIED, INTERNAL_ERROR, OK

DEFAULT_OUTPUT_DIR = Path("bench") / "results"
DEFAULT_JSON_NAME = "latest.json"
DEFAULT_CSV_NAME = "latest.csv"
DEFAULT_MATRIX_JSON_NAME = "matrix.json"
DEFAULT_MATRIX_CSV_NAME = "matrix.csv"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Agent Sentinel benchmark suite.")
    parser.add_argument(
        "--tasks-dir",
        default=DEFAULT_TASKS_DIR,
        help=f"Directory containing task specs (default: {DEFAULT_TASKS_DIR}).",
    )
    parser.add_argument(
        "--policy",
        default=DEFAULT_POLICY_PATH,
        help=f"Policy file path (default: {DEFAULT_POLICY_PATH}).",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Directory for benchmark outputs (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--json-name",
        default=DEFAULT_JSON_NAME,
        help=f"JSON filename to write under output-dir (default: {DEFAULT_JSON_NAME}).",
    )
    parser.add_argument(
        "--csv-name",
        default=DEFAULT_CSV_NAME,
        help=f"CSV filename to write under output-dir (default: {DEFAULT_CSV_NAME}).",
    )
    parser.add_argument(
        "--enable-trace",
        action="store_true",
        help="Enable trace recording during benchmark runs (default: off).",
    )
    parser.add_argument(
        "--disable-validation",
        action="store_true",
        help="Disable tool validation checks for ablation runs.",
    )
    parser.add_argument(
        "--disable-plugins",
        action="store_true",
        help="Disable plugin discovery for ablation runs.",
    )
    parser.add_argument(
        "--matrix",
        action="store_true",
        help="Run all ablation combinations and write matrix.json / matrix.csv.",
    )
    return parser


def _write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_csv_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    benchmark_id = str(report.get("benchmark_id", ""))
    tasks_total = int(report.get("tasks_total", 0))
    rows: list[dict[str, Any]] = []

    for mode in ("baseline", "secured"):
        mode_payload = report.get(mode, {})
        metrics = mode_payload.get("metrics", {}) if isinstance(mode_payload, dict) else {}
        if not isinstance(metrics, dict):
            continue
        for metric in sorted(metrics):
            rows.append(
                {
                    "benchmark_id": benchmark_id,
                    "tasks_total": tasks_total,
                    "mode": mode,
                    "metric": metric,
                    "value": metrics[metric],
                }
            )

    return rows


def _derive_exit_code(*, success: bool, blocked: bool) -> int:
    if success:
        return OK
    if blocked:
        return DENIED
    return INTERNAL_ERROR


def _summarize_run(
    *,
    report: dict[str, Any],
    trace_enabled: bool,
    validation_enabled: bool,
    plugins_enabled: bool,
) -> dict[str, Any]:
    latencies: list[float] = []
    failures = 0
    histogram: dict[int, int] = {}

    for mode in ("baseline", "secured"):
        mode_payload = report.get(mode, {})
        results = mode_payload.get("results", []) if isinstance(mode_payload, dict) else []
        if not isinstance(results, list):
            continue
        for result in results:
            if not isinstance(result, dict):
                continue
            success = bool(result.get("success", False))
            blocked = bool(result.get("blocked", False))
            exit_code = _derive_exit_code(success=success, blocked=blocked)
            histogram[exit_code] = histogram.get(exit_code, 0) + 1
            latencies.append(float(result.get("latency_ms", 0.0)))
            if not success:
                failures += 1

    avg_runtime = (sum(latencies) / len(latencies)) if latencies else 0.0
    mode_label = (
        f"trace={'on' if trace_enabled else 'off'}|"
        f"validation={'on' if validation_enabled else 'off'}|"
        f"plugins={'on' if plugins_enabled else 'off'}"
    )
    return {
        "mode_label": mode_label,
        "trace": "on" if trace_enabled else "off",
        "validation": "on" if validation_enabled else "off",
        "plugins": "on" if plugins_enabled else "off",
        "avg_runtime_ms": round(avg_runtime, 6),
        "exit_code_histogram": dict(sorted(histogram.items())),
        "failure_count": failures,
        "trace_event_count": int(report.get("trace_event_count", 0)),
    }


def _write_csv(path: Path, report: dict[str, Any]) -> None:
    rows = _build_csv_rows(report)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["benchmark_id", "tasks_total", "mode", "metric", "value"],
        )
        writer.writeheader()
        writer.writerows(rows)


def _write_matrix_json(path: Path, runs: list[dict[str, Any]]) -> None:
    payload = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "runs": sorted(runs, key=lambda row: str(row["mode_label"])),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_matrix_csv(path: Path, runs: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "mode_label",
                "trace",
                "validation",
                "plugins",
                "avg_runtime_ms",
                "exit_code_histogram",
                "failure_count",
                "trace_event_count",
            ],
        )
        writer.writeheader()
        for row in sorted(runs, key=lambda item: str(item["mode_label"])):
            writer.writerow(
                {
                    "mode_label": row["mode_label"],
                    "trace": row["trace"],
                    "validation": row["validation"],
                    "plugins": row["plugins"],
                    "avg_runtime_ms": row["avg_runtime_ms"],
                    "exit_code_histogram": json.dumps(
                        row["exit_code_histogram"],
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                    "failure_count": row["failure_count"],
                    "trace_event_count": row["trace_event_count"],
                }
            )


def run(
    *,
    tasks_dir: str = DEFAULT_TASKS_DIR,
    policy_path: str = DEFAULT_POLICY_PATH,
    output_dir: str = str(DEFAULT_OUTPUT_DIR),
    json_name: str = DEFAULT_JSON_NAME,
    csv_name: str = DEFAULT_CSV_NAME,
    enable_trace: bool = False,
    disable_validation: bool = False,
    disable_plugins: bool = False,
) -> tuple[Path, Path, dict[str, Any]]:
    report = execute_benchmark(
        tasks_dir=tasks_dir,
        policy_path=policy_path,
        enable_trace=enable_trace,
        enable_validation=not disable_validation,
        enable_plugins=not disable_plugins,
    )
    output_root = Path(output_dir)
    json_path = output_root / json_name
    csv_path = output_root / csv_name
    _write_json(json_path, report)
    _write_csv(csv_path, report)
    return json_path, csv_path, report


def run_matrix(
    *,
    tasks_dir: str = DEFAULT_TASKS_DIR,
    policy_path: str = DEFAULT_POLICY_PATH,
    output_dir: str = str(DEFAULT_OUTPUT_DIR),
) -> tuple[Path, Path, list[dict[str, Any]]]:
    runs: list[dict[str, Any]] = []

    for trace_enabled, validation_enabled, plugins_enabled in itertools.product(
        [False, True],
        [True, False],
        [True, False],
    ):
        with tempfile.TemporaryDirectory(prefix="agent-sentinel-matrix-") as temp_dir:
            report = execute_benchmark(
                tasks_dir=tasks_dir,
                policy_path=policy_path,
                enable_trace=trace_enabled,
                enable_validation=validation_enabled,
                enable_plugins=plugins_enabled,
                working_dir=temp_dir,
            )
        runs.append(
            _summarize_run(
                report=report,
                trace_enabled=trace_enabled,
                validation_enabled=validation_enabled,
                plugins_enabled=plugins_enabled,
            )
        )

    output_root = Path(output_dir)
    matrix_json_path = output_root / DEFAULT_MATRIX_JSON_NAME
    matrix_csv_path = output_root / DEFAULT_MATRIX_CSV_NAME
    _write_matrix_json(matrix_json_path, runs)
    _write_matrix_csv(matrix_csv_path, runs)
    return matrix_json_path, matrix_csv_path, runs


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.matrix:
        matrix_json_path, matrix_csv_path, _ = run_matrix(
            tasks_dir=args.tasks_dir,
            policy_path=args.policy,
            output_dir=args.output_dir,
        )
        print(f"Benchmark matrix written: {matrix_json_path} and {matrix_csv_path}")
        return 0

    json_path, csv_path, _ = run(
        tasks_dir=args.tasks_dir,
        policy_path=args.policy,
        output_dir=args.output_dir,
        json_name=args.json_name,
        csv_name=args.csv_name,
        enable_trace=args.enable_trace,
        disable_validation=args.disable_validation,
        disable_plugins=args.disable_plugins,
    )
    print(f"Benchmark results written: {json_path} and {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
