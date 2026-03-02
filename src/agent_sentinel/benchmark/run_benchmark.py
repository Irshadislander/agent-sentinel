from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from agent_sentinel.benchmark.runner import (
    DEFAULT_POLICY_PATH,
    DEFAULT_TASKS_DIR,
)
from agent_sentinel.benchmark.runner import (
    run_benchmark as execute_benchmark,
)

DEFAULT_OUTPUT_DIR = Path("bench") / "results"
DEFAULT_JSON_NAME = "latest.json"
DEFAULT_CSV_NAME = "latest.csv"


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


def run(
    *,
    tasks_dir: str = DEFAULT_TASKS_DIR,
    policy_path: str = DEFAULT_POLICY_PATH,
    output_dir: str = str(DEFAULT_OUTPUT_DIR),
    json_name: str = DEFAULT_JSON_NAME,
    csv_name: str = DEFAULT_CSV_NAME,
) -> tuple[Path, Path, dict[str, Any]]:
    report = execute_benchmark(tasks_dir=tasks_dir, policy_path=policy_path)
    output_root = Path(output_dir)
    json_path = output_root / json_name
    csv_path = output_root / csv_name
    _write_json(json_path, report)
    _write_csv(csv_path, report)
    return json_path, csv_path, report


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    json_path, csv_path, _ = run(
        tasks_dir=args.tasks_dir,
        policy_path=args.policy,
        output_dir=args.output_dir,
        json_name=args.json_name,
        csv_name=args.csv_name,
    )
    print(f"Benchmark results written: {json_path} and {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
