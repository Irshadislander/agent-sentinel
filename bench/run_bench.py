from __future__ import annotations

import argparse
import csv
import json
import math
import os
import statistics
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any

try:
    from agent_sentinel.observability import (
        TraceEvent,
        TraceStore,
        new_run_context,
        validate_payload_against_schema,
    )
except ModuleNotFoundError as exc:
    if exc.name and not exc.name.startswith("agent_sentinel"):
        raise
    repo_src = Path(__file__).resolve().parents[1] / "src"
    if repo_src.is_dir():
        sys.path.insert(0, str(repo_src))
    from agent_sentinel.observability import (
        TraceEvent,
        TraceStore,
        new_run_context,
        validate_payload_against_schema,
    )


@dataclass(frozen=True)
class MetricSummary:
    mean: float
    p50: float
    p95: float
    min: float
    max: float
    std: float


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python bench/run_bench.py")
    parser.add_argument("--iterations", type=int, default=50, help="Number of benchmark iterations")
    parser.add_argument(
        "--capability-id",
        default="core.example.echo",
        help="Capability id to execute for end-to-end run latency",
    )
    parser.add_argument(
        "--output-dir",
        default="bench/results",
        help="Output directory for latest.json/latest.csv",
    )
    return parser.parse_args(argv)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _run_cli(args: list[str], *, cwd: Path) -> tuple[float, subprocess.CompletedProcess[str]]:
    env = os.environ.copy()
    env.setdefault("PYTHONHASHSEED", "0")
    src_path = _repo_root() / "src"
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        str(src_path) if not existing_pythonpath else f"{src_path}:{existing_pythonpath}"
    )
    start = perf_counter()
    completed = subprocess.run(
        [sys.executable, "-m", "agent_sentinel.cli", "--no-plugins", *args],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
    )
    elapsed_ms = (perf_counter() - start) * 1000.0
    if completed.returncode != 0:
        raise RuntimeError(
            f"CLI command failed ({' '.join(args)}): "
            f"code={completed.returncode}, stderr={completed.stderr.strip()}"
        )
    return elapsed_ms, completed


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * percentile
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return ordered[low]
    weight = rank - low
    return ordered[low] + (ordered[high] - ordered[low]) * weight


def _summarize(values: list[float]) -> MetricSummary:
    if not values:
        return MetricSummary(mean=0.0, p50=0.0, p95=0.0, min=0.0, max=0.0, std=0.0)
    std = statistics.pstdev(values) if len(values) > 1 else 0.0
    return MetricSummary(
        mean=statistics.fmean(values),
        p50=_percentile(values, 0.50),
        p95=_percentile(values, 0.95),
        min=min(values),
        max=max(values),
        std=std,
    )


def _round_metrics(values: list[float]) -> list[float]:
    return [round(value, 6) for value in values]


def _collect_metrics(
    iterations: int,
    capability_id: str,
    *,
    cwd: Path,
    trace_path: Path,
) -> dict[str, list[float]]:
    from agent_sentinel.capabilities import plugins

    if trace_path.exists():
        trace_path.unlink()
    trace_store = TraceStore(trace_path)

    list_samples: list[float] = []
    run_samples: list[float] = []
    trace_view_samples: list[float] = []
    plugin_discovery_samples: list[float] = []
    payload_validation_samples: list[float] = []
    trace_overhead_samples: list[float] = []

    cold_start_ms, _ = _run_cli(["list"], cwd=cwd)

    for _ in range(iterations):
        elapsed, _ = _run_cli(["list"], cwd=cwd)
        list_samples.append(elapsed)

    for _ in range(iterations):
        elapsed, _ = _run_cli(
            [
                "run",
                capability_id,
                "--payload",
                "{}",
                "--trace-path",
                str(trace_path),
            ],
            cwd=cwd,
        )
        run_samples.append(elapsed)

    for _ in range(iterations):
        elapsed, _ = _run_cli(
            ["trace", "view", "--last", "20", "--trace-path", str(trace_path)],
            cwd=cwd,
        )
        trace_view_samples.append(elapsed)

    for _ in range(iterations):
        plugins._LOADED_ENTRYPOINTS.clear()
        start = perf_counter()
        plugins.load_capabilities(strict=False, warn=lambda _msg: None)
        plugin_discovery_samples.append((perf_counter() - start) * 1000.0)

    schema = {
        "type": "object",
        "properties": {"message": {"type": "string"}},
    }
    payload: dict[str, object] = {"message": "hello"}
    for _ in range(iterations):
        start = perf_counter()
        is_valid, _ = validate_payload_against_schema(payload, schema)
        payload_validation_samples.append((perf_counter() - start) * 1000.0)
        if not is_valid:
            raise RuntimeError("validation benchmark payload unexpectedly failed")

    for _ in range(iterations):
        context = new_run_context()
        event = TraceEvent(
            event_type="benchmark.trace.append",
            run_context=context,
            capability_id=capability_id,
            schema_version="1.0.0",
            validation_outcome="passed",
            duration_ms=0.0,
            exit_code=0,
            error_kind=None,
            error=None,
        )
        start = perf_counter()
        trace_store.append(event)
        trace_overhead_samples.append((perf_counter() - start) * 1000.0)

    warm_start_samples = list_samples[1:] if len(list_samples) > 1 else list_samples

    return {
        "capability_execution_e2e_ms": run_samples,
        "cli_cold_start_ms": [cold_start_ms],
        "cli_list_ms": list_samples,
        "cli_run_ms": run_samples,
        "cli_trace_view_ms": trace_view_samples,
        "cli_warm_start_ms": warm_start_samples,
        "payload_validation_ms": payload_validation_samples,
        "registry_plugin_discovery_ms": plugin_discovery_samples,
        "trace_observability_overhead_ms": trace_overhead_samples,
    }


def _build_report(
    *,
    iterations: int,
    capability_id: str,
    metrics: dict[str, list[float]],
) -> dict[str, Any]:
    report_metrics: dict[str, Any] = {}
    for metric_name in sorted(metrics):
        samples = metrics[metric_name]
        summary = _summarize(samples)
        report_metrics[metric_name] = {
            "samples": _round_metrics(samples),
            "stats": {
                "max": round(summary.max, 6),
                "mean": round(summary.mean, 6),
                "min": round(summary.min, 6),
                "p50": round(summary.p50, 6),
                "p95": round(summary.p95, 6),
                "std": round(summary.std, 6),
            },
            "unit": "ms",
        }

    return {
        "capability_id": capability_id,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "iterations": iterations,
        "metrics": report_metrics,
        "schema_version": "1",
    }


def _write_outputs(report: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "latest.json"
    csv_path = output_dir / "latest.csv"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["metric", "iterations", "mean", "p50", "p95", "min", "max", "std"],
        )
        writer.writeheader()
        for metric_name in sorted(report["metrics"]):
            stats = report["metrics"][metric_name]["stats"]
            writer.writerow(
                {
                    "metric": metric_name,
                    "iterations": report["iterations"],
                    "mean": stats["mean"],
                    "p50": stats["p50"],
                    "p95": stats["p95"],
                    "min": stats["min"],
                    "max": stats["max"],
                    "std": stats["std"],
                }
            )

    return json_path, csv_path


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.iterations <= 0:
        raise SystemExit("--iterations must be > 0")

    cwd = _repo_root()
    output_dir = Path(args.output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    trace_path = output_dir / "trace.jsonl"

    metrics = _collect_metrics(
        args.iterations,
        args.capability_id,
        cwd=cwd,
        trace_path=trace_path,
    )
    report = _build_report(
        iterations=args.iterations,
        capability_id=args.capability_id,
        metrics=metrics,
    )
    json_path, csv_path = _write_outputs(report, output_dir)
    print(f"Benchmark results written: {json_path} and {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
