from __future__ import annotations

import argparse
import csv
import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agent_sentinel.benchmark.runner import (
    DEFAULT_POLICY_PATH,
    DEFAULT_TASKS_DIR,
)
from agent_sentinel.benchmark.runner import run_benchmark as execute_benchmark
from agent_sentinel.cli_exit_codes import DENIED, INTERNAL_ERROR, OK

DEFAULT_OUTPUT_DIR = Path("bench") / "results"
DEFAULT_JSON_NAME = "latest.json"
DEFAULT_CSV_NAME = "latest.csv"
DEFAULT_MATRIX_JSON_NAME = "matrix.json"
DEFAULT_MATRIX_CSV_NAME = "matrix.csv"
BASELINES = ("default", "no_policy", "no_trace", "raw_errors", "no_plugin_isolation")


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
        "--baseline",
        choices=BASELINES,
        default="default",
        help="Benchmark baseline mode (default: default).",
    )
    parser.add_argument(
        "--baselines",
        default="",
        help=(
            "Comma-separated baseline list for matrix mode "
            "(e.g. default,no_policy,no_trace,raw_errors,no_plugin_isolation)."
        ),
    )
    parser.add_argument(
        "--matrix",
        action="store_true",
        help="Run matrix mode and write matrix.json / matrix.csv.",
    )
    parser.add_argument(
        "--matrix-all-baselines",
        action="store_true",
        help="In matrix mode, run all baseline variants.",
    )
    parser.add_argument(
        "--enable-trace",
        action="store_true",
        help="Enable trace recording (overrides baseline default).",
    )
    parser.add_argument(
        "--disable-validation",
        action="store_true",
        help="Disable tool validation checks (overrides baseline default).",
    )
    parser.add_argument(
        "--disable-plugins",
        action="store_true",
        help="Disable plugin discovery (overrides baseline default).",
    )
    return parser


def _parse_baselines(raw: str) -> list[str]:
    if not raw.strip():
        return []

    parsed: list[str] = []
    seen: set[str] = set()
    for value in raw.split(","):
        name = value.strip()
        if not name:
            continue
        if name not in BASELINES:
            raise ValueError(f"unknown baseline '{name}'")
        if name not in seen:
            parsed.append(name)
            seen.add(name)
    return parsed


def _baseline_options(baseline: str) -> dict[str, Any]:
    options: dict[str, dict[str, Any]] = {
        "default": {
            "enable_trace": True,
            "enable_validation": True,
            "enable_plugins": True,
            "enforce_policy": True,
            "structured_errors": True,
            "plugin_allowlist_enforced": True,
        },
        "no_policy": {
            "enable_trace": True,
            "enable_validation": True,
            "enable_plugins": True,
            "enforce_policy": False,
            "structured_errors": True,
            "plugin_allowlist_enforced": True,
        },
        "no_trace": {
            "enable_trace": False,
            "enable_validation": True,
            "enable_plugins": True,
            "enforce_policy": True,
            "structured_errors": True,
            "plugin_allowlist_enforced": True,
        },
        "raw_errors": {
            "enable_trace": True,
            "enable_validation": True,
            "enable_plugins": True,
            "enforce_policy": True,
            "structured_errors": False,
            "plugin_allowlist_enforced": True,
        },
        "no_plugin_isolation": {
            "enable_trace": True,
            "enable_validation": True,
            "enable_plugins": True,
            "enforce_policy": True,
            "structured_errors": True,
            "plugin_allowlist_enforced": False,
        },
    }
    return dict(options[baseline])


def _derive_exit_code(*, success: bool, blocked: bool) -> int:
    if success:
        return OK
    if blocked:
        return DENIED
    return INTERNAL_ERROR


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


def _error_kind(error: str, *, baseline: str) -> str:
    if not error:
        return "none"
    if baseline == "raw_errors":
        return "raw_error"
    if ":" in error:
        return error.split(":", 1)[0].strip().lower()
    return "unknown"


def _rows_for_baseline(report: dict[str, Any], *, baseline: str) -> list[dict[str, Any]]:
    secured = report.get("secured", {})
    secured_results = secured.get("results", []) if isinstance(secured, dict) else []
    if not isinstance(secured_results, list):
        secured_results = []

    has_trace = bool(report.get("flags", {}).get("trace_enabled", False))
    rows: list[dict[str, Any]] = []
    for result in secured_results:
        if not isinstance(result, dict):
            continue
        success = bool(result.get("success", False))
        blocked = bool(result.get("blocked", False))
        decision = "allow" if success else "deny"
        error = str(result.get("error", ""))
        rows.append(
            {
                "baseline": baseline,
                "task_id": str(result.get("task_name", "")),
                "category": str(result.get("category", "")),
                "decision": decision,
                "exit_code": _derive_exit_code(success=success, blocked=blocked),
                "duration_ms": round(float(result.get("latency_ms", 0.0)), 6),
                "has_trace": has_trace,
                "error_kind": _error_kind(error, baseline=baseline),
                "raw_error": error if baseline == "raw_errors" else "",
            }
        )
    return rows


def _write_matrix_json(path: Path, rows: list[dict[str, Any]]) -> None:
    sorted_rows = sorted(rows, key=lambda row: (str(row["baseline"]), str(row["task_id"])))
    grouped_rows: dict[str, list[dict[str, Any]]] = {}
    for row in sorted_rows:
        grouped_rows.setdefault(str(row["baseline"]), []).append(row)

    payload = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "baselines": grouped_rows,
        "rows": sorted_rows,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_matrix_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "baseline",
                "task_id",
                "category",
                "decision",
                "exit_code",
                "duration_ms",
                "has_trace",
                "error_kind",
                "raw_error",
            ],
        )
        writer.writeheader()
        for row in sorted(rows, key=lambda item: (str(item["baseline"]), str(item["task_id"]))):
            writer.writerow(row)


def run(
    *,
    tasks_dir: str = DEFAULT_TASKS_DIR,
    policy_path: str = DEFAULT_POLICY_PATH,
    output_dir: str = str(DEFAULT_OUTPUT_DIR),
    json_name: str = DEFAULT_JSON_NAME,
    csv_name: str = DEFAULT_CSV_NAME,
    baseline: str = "default",
    enable_trace_override: bool = False,
    disable_validation_override: bool = False,
    disable_plugins_override: bool = False,
) -> tuple[Path, Path, dict[str, Any]]:
    options = _baseline_options(baseline)
    options["enable_trace"] = bool(options["enable_trace"] or enable_trace_override)
    options["enable_validation"] = bool(
        options["enable_validation"] and not disable_validation_override
    )
    options["enable_plugins"] = bool(options["enable_plugins"] and not disable_plugins_override)

    report = execute_benchmark(
        tasks_dir=tasks_dir,
        policy_path=policy_path,
        enable_trace=bool(options["enable_trace"]),
        enable_validation=bool(options["enable_validation"]),
        enable_plugins=bool(options["enable_plugins"]),
        enforce_policy=bool(options["enforce_policy"]),
        structured_errors=bool(options["structured_errors"]),
        plugin_allowlist_enforced=bool(options["plugin_allowlist_enforced"]),
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
    baselines: list[str] | None = None,
) -> tuple[Path, Path, list[dict[str, Any]]]:
    selected = list(baselines) if baselines else ["default"]
    rows: list[dict[str, Any]] = []

    for baseline in selected:
        options = _baseline_options(baseline)
        with tempfile.TemporaryDirectory(prefix="agent-sentinel-matrix-") as temp_dir:
            report = execute_benchmark(
                tasks_dir=tasks_dir,
                policy_path=policy_path,
                enable_trace=bool(options["enable_trace"]),
                enable_validation=bool(options["enable_validation"]),
                enable_plugins=bool(options["enable_plugins"]),
                enforce_policy=bool(options["enforce_policy"]),
                structured_errors=bool(options["structured_errors"]),
                plugin_allowlist_enforced=bool(options["plugin_allowlist_enforced"]),
                working_dir=temp_dir,
            )
        rows.extend(_rows_for_baseline(report, baseline=baseline))

    output_root = Path(output_dir)
    matrix_json_path = output_root / DEFAULT_MATRIX_JSON_NAME
    matrix_csv_path = output_root / DEFAULT_MATRIX_CSV_NAME
    _write_matrix_json(matrix_json_path, rows)
    _write_matrix_csv(matrix_csv_path, rows)
    return matrix_json_path, matrix_csv_path, rows


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.matrix:
        if args.matrix_all_baselines:
            selected_baselines = list(BASELINES)
        elif args.baselines:
            try:
                selected_baselines = _parse_baselines(args.baselines)
            except ValueError as exc:
                parser.error(str(exc))
        else:
            selected_baselines = [args.baseline]

        matrix_json_path, matrix_csv_path, _ = run_matrix(
            tasks_dir=args.tasks_dir,
            policy_path=args.policy,
            output_dir=args.output_dir,
            baselines=selected_baselines,
        )
        print(f"Benchmark matrix written: {matrix_json_path} and {matrix_csv_path}")
        return 0

    json_path, csv_path, _ = run(
        tasks_dir=args.tasks_dir,
        policy_path=args.policy,
        output_dir=args.output_dir,
        json_name=args.json_name,
        csv_name=args.csv_name,
        baseline=args.baseline,
        enable_trace_override=args.enable_trace,
        disable_validation_override=args.disable_validation,
        disable_plugins_override=args.disable_plugins,
    )
    print(f"Benchmark results written: {json_path} and {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
