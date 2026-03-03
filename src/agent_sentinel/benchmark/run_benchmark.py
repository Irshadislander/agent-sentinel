from __future__ import annotations

import argparse
import csv
import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agent_sentinel.benchmark.policy_engine_perf import (
    run_policy_engine_benchmark,
    write_policy_engine_benchmark_outputs,
)
from agent_sentinel.benchmark.runner import (
    DEFAULT_POLICY_PATH,
    DEFAULT_TASKS_DIR,
)
from agent_sentinel.benchmark.runner import run_benchmark as execute_benchmark
from agent_sentinel.benchmark.synthetic import DEFAULT_MIX, generate_synthetic_tasks
from agent_sentinel.cli_exit_codes import DENIED, INTERNAL_ERROR, OK

DEFAULT_OUTPUT_DIR = Path("bench") / "results"
DEFAULT_JSON_NAME = "latest.json"
DEFAULT_CSV_NAME = "latest.csv"
DEFAULT_MATRIX_JSON_NAME = "matrix.json"
DEFAULT_MATRIX_CSV_NAME = "matrix.csv"
DEFAULT_SYNTHETIC_OUT_DIR = "configs/tasks_synth"
BASELINES = ("default", "no_policy", "no_trace", "raw_errors", "no_plugin_isolation")


@dataclass(frozen=True)
class ScenarioConfig:
    scenario_id: str
    tasks_dir: str
    synthetic_n: int
    synthetic_seed: int
    synthetic_out_dir: str
    noise_malformed_p: float
    noise_plugin_p: float
    policy_strictness: str
    trace_sample_rate: float
    allowlist_size: int


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
        "--scenarios",
        default="",
        help=(
            "Comma-separated scenario sweep identifiers "
            "(e.g. scale_n50,stress_m0.10_p0.05,sens_strict=high_trace=0.5_allow=1,"
            "policy_engine_perf)."
        ),
    )
    parser.add_argument(
        "--synthetic",
        type=int,
        default=0,
        help="Number of synthetic tasks to generate (default: 0).",
    )
    parser.add_argument(
        "--synthetic-seed",
        type=int,
        default=0,
        help="Seed for deterministic synthetic task generation (default: 0).",
    )
    parser.add_argument(
        "--synthetic-out-dir",
        default=DEFAULT_SYNTHETIC_OUT_DIR,
        help=f"Directory to write synthetic tasks (default: {DEFAULT_SYNTHETIC_OUT_DIR}).",
    )
    parser.add_argument(
        "--noise",
        type=float,
        default=0.0,
        help="Malformed-payload noise probability (default: 0.0).",
    )
    parser.add_argument(
        "--noise-plugin-p",
        "--noise-PLUGIN_P",
        dest="noise_plugin_p",
        type=float,
        default=0.0,
        help="Plugin-violation noise probability (default: 0.0).",
    )
    parser.add_argument(
        "--policy-strictness",
        choices=("low", "medium", "high"),
        default="medium",
        help="Policy strictness mode (default: medium).",
    )
    parser.add_argument(
        "--trace-sample-rate",
        type=float,
        default=1.0,
        help="Trace sampling rate in [0,1] (default: 1.0).",
    )
    parser.add_argument(
        "--allowlist-size",
        type=int,
        default=-1,
        help="Plugin allowlist cap; -1 means no cap (default: -1).",
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


def _validate_probability(name: str, value: float) -> float:
    if value < 0.0 or value > 1.0:
        raise ValueError(f"{name} must be in [0,1]")
    return value


def _default_scenario_id(config: ScenarioConfig) -> str:
    if config.synthetic_n > 0:
        return f"scale_n{config.synthetic_n}"
    if config.noise_malformed_p > 0.0 or config.noise_plugin_p > 0.0:
        return f"stress_m{config.noise_malformed_p:.2f}_p{config.noise_plugin_p:.2f}"
    if (
        config.policy_strictness != "medium"
        or config.trace_sample_rate != 1.0
        or config.allowlist_size >= 0
    ):
        return (
            "sens_"
            f"strict={config.policy_strictness}"
            f"_trace={config.trace_sample_rate}"
            f"_allow={config.allowlist_size}"
        )
    return "default"


def _base_scenario(
    *,
    tasks_dir: str,
    synthetic_n: int,
    synthetic_seed: int,
    synthetic_out_dir: str,
    noise_malformed_p: float,
    noise_plugin_p: float,
    policy_strictness: str,
    trace_sample_rate: float,
    allowlist_size: int,
) -> ScenarioConfig:
    base = ScenarioConfig(
        scenario_id="",
        tasks_dir=tasks_dir,
        synthetic_n=synthetic_n,
        synthetic_seed=synthetic_seed,
        synthetic_out_dir=synthetic_out_dir,
        noise_malformed_p=_validate_probability("noise", noise_malformed_p),
        noise_plugin_p=_validate_probability("noise_plugin_p", noise_plugin_p),
        policy_strictness=policy_strictness,
        trace_sample_rate=_validate_probability("trace_sample_rate", trace_sample_rate),
        allowlist_size=allowlist_size,
    )
    return ScenarioConfig(**{**base.__dict__, "scenario_id": _default_scenario_id(base)})


def _parse_scenarios(raw: str, base: ScenarioConfig) -> list[ScenarioConfig]:
    if not raw.strip():
        return [base]

    scenarios: list[ScenarioConfig] = []
    for idx, token in enumerate(raw.split(",")):
        value = token.strip()
        if not value:
            continue
        scenario = base
        if value == "default":
            scenario = ScenarioConfig(**{**base.__dict__, "scenario_id": "default"})
        elif value.startswith("scale_n"):
            match = re.fullmatch(r"scale_n(\d+)", value)
            if not match:
                raise ValueError(f"invalid scenario token: {value}")
            n = int(match.group(1))
            scenario = ScenarioConfig(
                **{
                    **base.__dict__,
                    "scenario_id": value,
                    "synthetic_n": n,
                    "synthetic_seed": base.synthetic_seed + idx,
                }
            )
        elif value.startswith("stress_"):
            match = re.fullmatch(r"stress_m([0-9.]+)_p([0-9.]+)", value)
            if not match:
                raise ValueError(f"invalid scenario token: {value}")
            scenario = ScenarioConfig(
                **{
                    **base.__dict__,
                    "scenario_id": value,
                    "noise_malformed_p": _validate_probability("noise", float(match.group(1))),
                    "noise_plugin_p": _validate_probability(
                        "noise_plugin_p", float(match.group(2))
                    ),
                }
            )
        elif value.startswith("sens_"):
            match = re.fullmatch(
                r"sens_strict=(low|medium|high)_trace=([0-9.]+)_allow=(-?\d+)", value
            )
            if not match:
                raise ValueError(f"invalid scenario token: {value}")
            scenario = ScenarioConfig(
                **{
                    **base.__dict__,
                    "scenario_id": value,
                    "policy_strictness": str(match.group(1)),
                    "trace_sample_rate": _validate_probability(
                        "trace_sample_rate", float(match.group(2))
                    ),
                    "allowlist_size": int(match.group(3)),
                }
            )
        elif value == "policy_engine_perf":
            scenario = ScenarioConfig(
                **{
                    **base.__dict__,
                    "scenario_id": "policy_engine_perf",
                    "synthetic_n": 0,
                }
            )
        else:
            raise ValueError(f"invalid scenario token: {value}")

        scenarios.append(scenario)

    if not scenarios:
        return [base]
    return scenarios


def _resolve_tasks_dir(config: ScenarioConfig) -> str:
    if config.synthetic_n <= 0:
        return config.tasks_dir

    out_dir = Path(config.synthetic_out_dir) / config.scenario_id
    mix = dict(DEFAULT_MIX)
    mix["malformed_payload"] = mix.get("malformed_payload", 0.1) + config.noise_malformed_p
    mix["plugin_violation"] = mix.get("plugin_violation", 0.1) + config.noise_plugin_p
    generate_synthetic_tasks(
        out_dir=str(out_dir),
        n=config.synthetic_n,
        seed=config.synthetic_seed,
        mix=mix,
    )
    return str(out_dir)


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


def _rows_for_baseline(
    report: dict[str, Any],
    *,
    baseline: str,
    scenario: ScenarioConfig,
) -> list[dict[str, Any]]:
    secured = report.get("secured", {})
    secured_results = secured.get("results", []) if isinstance(secured, dict) else []
    if not isinstance(secured_results, list):
        secured_results = []

    plugin_count = int(report.get("plugin_entrypoint_count", 0))
    rows: list[dict[str, Any]] = []
    for result in secured_results:
        if not isinstance(result, dict):
            continue
        success = bool(result.get("success", False))
        blocked = bool(result.get("blocked", False))
        decision = "allow" if success else "deny"
        error = str(result.get("error", ""))
        has_trace = bool(
            result.get("traced", bool(report.get("flags", {}).get("trace_enabled", False)))
        )
        rows.append(
            {
                "baseline": baseline,
                "scenario_id": scenario.scenario_id,
                "task_id": str(result.get("task_name", "")),
                "category": str(result.get("category", "")),
                "decision": decision,
                "exit_code": _derive_exit_code(success=success, blocked=blocked),
                "duration_ms": round(float(result.get("latency_ms", 0.0)), 6),
                "has_trace": has_trace,
                "plugin_entrypoint_count": plugin_count,
                "error_kind": _error_kind(error, baseline=baseline),
                "raw_error": error if baseline == "raw_errors" else "",
                "synthetic_n": scenario.synthetic_n,
                "noise_malformed_p": scenario.noise_malformed_p,
                "noise_plugin_p": scenario.noise_plugin_p,
                "policy_strictness": scenario.policy_strictness,
                "trace_sample_rate": scenario.trace_sample_rate,
                "allowlist_size": scenario.allowlist_size,
            }
        )
    return rows


def _rows_for_policy_engine_perf(
    payload: dict[str, Any],
    *,
    baseline: str,
    scenario: ScenarioConfig,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    raw_cases = payload.get("cases", [])
    if not isinstance(raw_cases, list):
        return rows

    for case in raw_cases:
        if not isinstance(case, dict):
            continue

        decision = str(case.get("decision", "deny")).lower()
        rows.append(
            {
                "baseline": baseline,
                "scenario_id": scenario.scenario_id,
                "task_id": str(case.get("case_id", "")),
                "category": "policy_engine_perf",
                "decision": decision,
                "exit_code": OK if decision == "allow" else DENIED,
                "duration_ms": round(float(case.get("mean_ms", 0.0)), 6),
                "has_trace": True,
                "plugin_entrypoint_count": 0,
                "error_kind": "none",
                "raw_error": "",
                "synthetic_n": scenario.synthetic_n,
                "noise_malformed_p": scenario.noise_malformed_p,
                "noise_plugin_p": scenario.noise_plugin_p,
                "policy_strictness": scenario.policy_strictness,
                "trace_sample_rate": scenario.trace_sample_rate,
                "allowlist_size": scenario.allowlist_size,
                "reason_code": str(case.get("reason_code", "")),
                "rule_id": str(case.get("rule_id") or ""),
                "p50_ms": round(float(case.get("p50_ms", 0.0)), 6),
                "p95_ms": round(float(case.get("p95_ms", 0.0)), 6),
                "p99_ms": round(float(case.get("p99_ms", 0.0)), 6),
                "trace_len_mean": round(float(case.get("trace_len_mean", 0.0)), 6),
            }
        )
    return rows


def _write_matrix_json(path: Path, rows: list[dict[str, Any]]) -> None:
    sorted_rows = sorted(
        rows,
        key=lambda row: (
            str(row["baseline"]),
            str(row["scenario_id"]),
            str(row["task_id"]),
        ),
    )
    baseline_grouped: dict[str, dict[str, list[dict[str, Any]]]] = {}
    scenario_grouped: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for row in sorted_rows:
        baseline = str(row["baseline"])
        scenario_id = str(row["scenario_id"])
        baseline_grouped.setdefault(baseline, {}).setdefault(scenario_id, []).append(row)
        scenario_grouped.setdefault(scenario_id, {}).setdefault(baseline, []).append(row)

    payload = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "grouped": baseline_grouped,
        "scenarios": scenario_grouped,
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
                "scenario_id",
                "task_id",
                "category",
                "decision",
                "exit_code",
                "duration_ms",
                "has_trace",
                "plugin_entrypoint_count",
                "error_kind",
                "raw_error",
                "synthetic_n",
                "noise_malformed_p",
                "noise_plugin_p",
                "policy_strictness",
                "trace_sample_rate",
                "allowlist_size",
                "reason_code",
                "rule_id",
                "p50_ms",
                "p95_ms",
                "p99_ms",
                "trace_len_mean",
            ],
        )
        writer.writeheader()
        for row in sorted(
            rows,
            key=lambda item: (
                str(item["baseline"]),
                str(item["scenario_id"]),
                str(item["task_id"]),
            ),
        ):
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
    synthetic: int = 0,
    synthetic_seed: int = 0,
    synthetic_out_dir: str = DEFAULT_SYNTHETIC_OUT_DIR,
    noise_malformed_p: float = 0.0,
    noise_plugin_p: float = 0.0,
    policy_strictness: str = "medium",
    trace_sample_rate: float = 1.0,
    allowlist_size: int = -1,
) -> tuple[Path, Path, dict[str, Any]]:
    options = _baseline_options(baseline)
    options["enable_trace"] = bool(options["enable_trace"] or enable_trace_override)
    options["enable_validation"] = bool(
        options["enable_validation"] and not disable_validation_override
    )
    options["enable_plugins"] = bool(options["enable_plugins"] and not disable_plugins_override)

    scenario = _base_scenario(
        tasks_dir=tasks_dir,
        synthetic_n=synthetic,
        synthetic_seed=synthetic_seed,
        synthetic_out_dir=synthetic_out_dir,
        noise_malformed_p=noise_malformed_p,
        noise_plugin_p=noise_plugin_p,
        policy_strictness=policy_strictness,
        trace_sample_rate=trace_sample_rate,
        allowlist_size=allowlist_size,
    )
    resolved_tasks_dir = _resolve_tasks_dir(scenario)

    report = execute_benchmark(
        tasks_dir=resolved_tasks_dir,
        policy_path=policy_path,
        enable_trace=bool(options["enable_trace"]),
        enable_validation=bool(options["enable_validation"]),
        enable_plugins=bool(options["enable_plugins"]),
        enforce_policy=bool(options["enforce_policy"]),
        structured_errors=bool(options["structured_errors"]),
        plugin_allowlist_enforced=bool(options["plugin_allowlist_enforced"]),
        noise_malformed_p=scenario.noise_malformed_p,
        noise_plugin_p=scenario.noise_plugin_p,
        random_seed=scenario.synthetic_seed,
        policy_strictness=scenario.policy_strictness,
        trace_sample_rate=scenario.trace_sample_rate,
        allowlist_size=scenario.allowlist_size,
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
    scenarios: list[ScenarioConfig] | None = None,
) -> tuple[Path, Path, list[dict[str, Any]]]:
    selected = list(baselines) if baselines else ["default"]
    selected_scenarios = (
        list(scenarios)
        if scenarios
        else [
            _base_scenario(
                tasks_dir=tasks_dir,
                synthetic_n=0,
                synthetic_seed=0,
                synthetic_out_dir=DEFAULT_SYNTHETIC_OUT_DIR,
                noise_malformed_p=0.0,
                noise_plugin_p=0.0,
                policy_strictness="medium",
                trace_sample_rate=1.0,
                allowlist_size=-1,
            )
        ]
    )
    rows: list[dict[str, Any]] = []

    for scenario in selected_scenarios:
        for baseline in selected:
            if scenario.scenario_id == "policy_engine_perf":
                perf_iterations = int(os.getenv("AGENT_SENTINEL_POLICY_PERF_ITERATIONS", "5000"))
                perf_warmup = int(os.getenv("AGENT_SENTINEL_POLICY_PERF_WARMUP", "200"))
                perf_payload = run_policy_engine_benchmark(
                    iterations=perf_iterations,
                    warmup=perf_warmup,
                )
                perf_dir = Path(output_dir) / "policy_engine_perf"
                write_policy_engine_benchmark_outputs(
                    perf_payload,
                    json_path=perf_dir / f"{baseline}.json",
                    markdown_path=perf_dir / f"{baseline}.md",
                )
                rows.extend(
                    _rows_for_policy_engine_perf(
                        perf_payload,
                        baseline=baseline,
                        scenario=scenario,
                    )
                )
                continue

            options = _baseline_options(baseline)
            resolved_tasks_dir = _resolve_tasks_dir(scenario)
            with tempfile.TemporaryDirectory(prefix="agent-sentinel-matrix-") as temp_dir:
                report = execute_benchmark(
                    tasks_dir=resolved_tasks_dir,
                    policy_path=policy_path,
                    enable_trace=bool(options["enable_trace"]),
                    enable_validation=bool(options["enable_validation"]),
                    enable_plugins=bool(options["enable_plugins"]),
                    enforce_policy=bool(options["enforce_policy"]),
                    structured_errors=bool(options["structured_errors"]),
                    plugin_allowlist_enforced=bool(options["plugin_allowlist_enforced"]),
                    working_dir=temp_dir,
                    noise_malformed_p=scenario.noise_malformed_p,
                    noise_plugin_p=scenario.noise_plugin_p,
                    random_seed=scenario.synthetic_seed,
                    policy_strictness=scenario.policy_strictness,
                    trace_sample_rate=scenario.trace_sample_rate,
                    allowlist_size=scenario.allowlist_size,
                )
            rows.extend(_rows_for_baseline(report, baseline=baseline, scenario=scenario))

    output_root = Path(output_dir)
    matrix_json_path = output_root / DEFAULT_MATRIX_JSON_NAME
    matrix_csv_path = output_root / DEFAULT_MATRIX_CSV_NAME
    _write_matrix_json(matrix_json_path, rows)
    _write_matrix_csv(matrix_csv_path, rows)
    return matrix_json_path, matrix_csv_path, rows


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        base_scenario = _base_scenario(
            tasks_dir=args.tasks_dir,
            synthetic_n=args.synthetic,
            synthetic_seed=args.synthetic_seed,
            synthetic_out_dir=args.synthetic_out_dir,
            noise_malformed_p=args.noise,
            noise_plugin_p=args.noise_plugin_p,
            policy_strictness=args.policy_strictness,
            trace_sample_rate=args.trace_sample_rate,
            allowlist_size=args.allowlist_size,
        )
    except ValueError as exc:
        parser.error(str(exc))

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

        try:
            scenario_sweep = _parse_scenarios(args.scenarios, base_scenario)
        except ValueError as exc:
            parser.error(str(exc))

        matrix_json_path, matrix_csv_path, _ = run_matrix(
            tasks_dir=args.tasks_dir,
            policy_path=args.policy,
            output_dir=args.output_dir,
            baselines=selected_baselines,
            scenarios=scenario_sweep,
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
        synthetic=args.synthetic,
        synthetic_seed=args.synthetic_seed,
        synthetic_out_dir=args.synthetic_out_dir,
        noise_malformed_p=args.noise,
        noise_plugin_p=args.noise_plugin_p,
        policy_strictness=args.policy_strictness,
        trace_sample_rate=args.trace_sample_rate,
        allowlist_size=args.allowlist_size,
    )
    print(f"Benchmark results written: {json_path} and {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
