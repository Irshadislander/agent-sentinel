from __future__ import annotations

import argparse
import csv
import glob
import json
import statistics
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_INPUT_GLOB = "bench/results/day12_seed_*/matrix.json"
DEFAULT_OUTPUT_JSON = Path("bench/results/day12_aggregate.json")
DEFAULT_OUTPUT_CSV = Path("bench/results/day12_aggregate.csv")
DEFAULT_RESULTS_MD = Path("paper/RESULTS_DAY12.md")
DEFAULT_APPENDIX_MD = Path("paper/APPENDIX_DAY12.md")
UER_DENIED_CATEGORIES = {"malicious", "policy_blocked"}


@dataclass(frozen=True)
class SeedSummary:
    seed_id: str
    baseline: str
    scenario_id: str
    uer: float
    far: float
    tcr: float
    eds: float
    plugin_loads: float
    latency_p50_ms: float
    latency_p95_ms: float


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    index = (len(ordered) - 1) * p
    low = int(index)
    high = min(low + 1, len(ordered) - 1)
    weight = index - low
    return ordered[low] + (ordered[high] - ordered[low]) * weight


def _mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    if len(values) == 1:
        return values[0], 0.0
    return statistics.mean(values), statistics.pstdev(values)


def _load_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _metrics(rows: list[dict[str, Any]]) -> tuple[float, float, float, float]:
    total = len(rows)
    if total == 0:
        return 0.0, 0.0, 0.0, 0.0

    denied_expected = [
        row for row in rows if str(row.get("category", "")).strip() in UER_DENIED_CATEGORIES
    ]
    denied_but_executed = sum(1 for row in denied_expected if row.get("decision") == "allow")
    uer = denied_but_executed / len(denied_expected) if denied_expected else 0.0

    failures = [row for row in rows if int(row.get("exit_code", 0)) != 0]
    ambiguous = sum(
        1
        for row in failures
        if str(row.get("error_kind", "")).lower() in {"", "none", "unknown", "raw_error"}
    )
    far = ambiguous / len(failures) if failures else 0.0

    traced = sum(1 for row in rows if bool(row.get("has_trace")))
    tcr = traced / total

    by_task: dict[str, set[int]] = {}
    for row in rows:
        task_id = str(row.get("task_id", ""))
        by_task.setdefault(task_id, set()).add(int(row.get("exit_code", 0)))
    consistent = sum(1 for codes in by_task.values() if len(codes) == 1)
    eds = consistent / len(by_task) if by_task else 0.0

    return uer, far, tcr, eds


def _summaries_for_seed(seed_id: str, rows: list[dict[str, Any]]) -> list[SeedSummary]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        baseline = str(row.get("baseline", "")).strip() or "unknown"
        scenario_id = str(row.get("scenario_id", "")).strip() or "default"
        grouped.setdefault((baseline, scenario_id), []).append(row)

    summaries: list[SeedSummary] = []
    for (baseline, scenario_id), group_rows in sorted(grouped.items()):
        latencies = [float(row.get("duration_ms", 0.0)) for row in group_rows]
        uer, far, tcr, eds = _metrics(group_rows)
        summaries.append(
            SeedSummary(
                seed_id=seed_id,
                baseline=baseline,
                scenario_id=scenario_id,
                uer=uer,
                far=far,
                tcr=tcr,
                eds=eds,
                plugin_loads=float(
                    max(int(row.get("plugin_entrypoint_count", 0)) for row in group_rows)
                    if group_rows
                    else 0
                ),
                latency_p50_ms=_percentile(latencies, 0.50),
                latency_p95_ms=_percentile(latencies, 0.95),
            )
        )
    return summaries


def _write_csv(path: Path, groups: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "baseline",
                "scenario_id",
                "seed_count",
                "uer_mean",
                "uer_std",
                "far_mean",
                "far_std",
                "tcr_mean",
                "tcr_std",
                "eds_mean",
                "eds_std",
                "plugin_loads_mean",
                "plugin_loads_std",
                "latency_p50_ms_mean",
                "latency_p50_ms_std",
                "latency_p95_ms_mean",
                "latency_p95_ms_std",
            ],
        )
        writer.writeheader()
        for group in groups:
            metrics = group.get("metrics", {})
            if not isinstance(metrics, dict):
                continue
            writer.writerow(
                {
                    "baseline": group.get("baseline", "unknown"),
                    "scenario_id": group.get("scenario_id", "default"),
                    "seed_count": group.get("seed_count", 0),
                    "uer_mean": metrics.get("uer_mean", 0.0),
                    "uer_std": metrics.get("uer_std", 0.0),
                    "far_mean": metrics.get("far_mean", 0.0),
                    "far_std": metrics.get("far_std", 0.0),
                    "tcr_mean": metrics.get("tcr_mean", 0.0),
                    "tcr_std": metrics.get("tcr_std", 0.0),
                    "eds_mean": metrics.get("eds_mean", 0.0),
                    "eds_std": metrics.get("eds_std", 0.0),
                    "plugin_loads_mean": metrics.get("plugin_loads_mean", 0.0),
                    "plugin_loads_std": metrics.get("plugin_loads_std", 0.0),
                    "latency_p50_ms_mean": metrics.get("latency_p50_ms_mean", 0.0),
                    "latency_p50_ms_std": metrics.get("latency_p50_ms_std", 0.0),
                    "latency_p95_ms_mean": metrics.get("latency_p95_ms_mean", 0.0),
                    "latency_p95_ms_std": metrics.get("latency_p95_ms_std", 0.0),
                }
            )
    return path


def _write_markdown_summaries(
    *,
    groups: list[dict[str, Any]],
    results_path: Path,
    appendix_path: Path,
) -> tuple[Path, Path]:
    results_lines = [
        "# Day 12 Results Summary",
        "",
        "## Key Deltas (mean ± std)",
        "",
    ]

    grouped_by_scenario: dict[str, dict[str, dict[str, Any]]] = {}
    for group in groups:
        scenario_id = str(group.get("scenario_id", "default"))
        baseline = str(group.get("baseline", "unknown"))
        grouped_by_scenario.setdefault(scenario_id, {})[baseline] = group

    for scenario_id in sorted(grouped_by_scenario):
        scenario_groups = grouped_by_scenario[scenario_id]
        default_group = scenario_groups.get("default")
        if not default_group:
            continue
        default_metrics = default_group.get("metrics", {})
        if not isinstance(default_metrics, dict):
            continue

        results_lines.append(f"### {scenario_id}")
        for baseline in sorted(scenario_groups):
            if baseline == "default":
                continue
            metrics = scenario_groups[baseline].get("metrics", {})
            if not isinstance(metrics, dict):
                continue
            results_lines.append(
                "- "
                f"{baseline}: "
                f"ΔUER={float(metrics.get('uer_mean', 0.0)) - float(default_metrics.get('uer_mean', 0.0)):+.4f}, "
                f"ΔFAR={float(metrics.get('far_mean', 0.0)) - float(default_metrics.get('far_mean', 0.0)):+.4f}, "
                f"ΔTCR={float(metrics.get('tcr_mean', 0.0)) - float(default_metrics.get('tcr_mean', 0.0)):+.4f}, "
                f"ΔEDS={float(metrics.get('eds_mean', 0.0)) - float(default_metrics.get('eds_mean', 0.0)):+.4f}"
            )
        results_lines.append("")

    appendix_lines = [
        "# Day 12 Appendix",
        "",
        "| baseline | scenario_id | seeds | UER mean±std | FAR mean±std | TCR mean±std | EDS mean±std | plugin_loads mean±std | p50 latency mean±std | p95 latency mean±std |",
        "|---|---|---:|---|---|---|---|---|---|---|",
    ]

    for group in sorted(
        groups, key=lambda g: (str(g.get("scenario_id", "")), str(g.get("baseline", "")))
    ):
        metrics = group.get("metrics", {})
        if not isinstance(metrics, dict):
            continue
        appendix_lines.append(
            "| "
            + " | ".join(
                [
                    str(group.get("baseline", "unknown")),
                    str(group.get("scenario_id", "default")),
                    str(group.get("seed_count", 0)),
                    f"{float(metrics.get('uer_mean', 0.0)):.4f} ± {float(metrics.get('uer_std', 0.0)):.4f}",
                    f"{float(metrics.get('far_mean', 0.0)):.4f} ± {float(metrics.get('far_std', 0.0)):.4f}",
                    f"{float(metrics.get('tcr_mean', 0.0)):.4f} ± {float(metrics.get('tcr_std', 0.0)):.4f}",
                    f"{float(metrics.get('eds_mean', 0.0)):.4f} ± {float(metrics.get('eds_std', 0.0)):.4f}",
                    f"{float(metrics.get('plugin_loads_mean', 0.0)):.2f} ± {float(metrics.get('plugin_loads_std', 0.0)):.2f}",
                    f"{float(metrics.get('latency_p50_ms_mean', 0.0)):.3f} ± {float(metrics.get('latency_p50_ms_std', 0.0)):.3f}",
                    f"{float(metrics.get('latency_p95_ms_mean', 0.0)):.3f} ± {float(metrics.get('latency_p95_ms_std', 0.0)):.3f}",
                ]
            )
            + " |"
        )

    results_path.parent.mkdir(parents=True, exist_ok=True)
    appendix_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text("\n".join(results_lines) + "\n", encoding="utf-8")
    appendix_path.write_text("\n".join(appendix_lines) + "\n", encoding="utf-8")
    return results_path, appendix_path


def merge_day12_seeds(
    input_glob: str,
    output_json: Path,
    output_csv: Path,
    results_path: Path,
    appendix_path: Path,
) -> tuple[Path, Path, Path, Path]:
    matrix_paths = [Path(path) for path in sorted(glob.glob(input_glob))]
    if not matrix_paths:
        raise ValueError(f"no matrix files matched pattern: {input_glob}")

    grouped: dict[tuple[str, str], list[SeedSummary]] = {}
    for matrix_path in matrix_paths:
        seed_id = matrix_path.parent.name
        rows = _load_rows(matrix_path)
        for summary in _summaries_for_seed(seed_id, rows):
            grouped.setdefault((summary.baseline, summary.scenario_id), []).append(summary)

    groups: list[dict[str, Any]] = []
    for (baseline, scenario_id), summaries in sorted(grouped.items()):
        uer_values = [s.uer for s in summaries]
        far_values = [s.far for s in summaries]
        tcr_values = [s.tcr for s in summaries]
        eds_values = [s.eds for s in summaries]
        plugin_values = [s.plugin_loads for s in summaries]
        latency_p50_values = [s.latency_p50_ms for s in summaries]
        latency_p95_values = [s.latency_p95_ms for s in summaries]

        uer_mean, uer_std = _mean_std(uer_values)
        far_mean, far_std = _mean_std(far_values)
        tcr_mean, tcr_std = _mean_std(tcr_values)
        eds_mean, eds_std = _mean_std(eds_values)
        plugin_mean, plugin_std = _mean_std(plugin_values)
        latency_p50_mean, latency_p50_std = _mean_std(latency_p50_values)
        latency_p95_mean, latency_p95_std = _mean_std(latency_p95_values)

        groups.append(
            {
                "baseline": baseline,
                "scenario_id": scenario_id,
                "seed_count": len(summaries),
                "metrics": {
                    "uer_mean": uer_mean,
                    "uer_std": uer_std,
                    "far_mean": far_mean,
                    "far_std": far_std,
                    "tcr_mean": tcr_mean,
                    "tcr_std": tcr_std,
                    "eds_mean": eds_mean,
                    "eds_std": eds_std,
                    "plugin_loads_mean": plugin_mean,
                    "plugin_loads_std": plugin_std,
                    "latency_p50_ms_mean": latency_p50_mean,
                    "latency_p50_ms_std": latency_p50_std,
                    "latency_p95_ms_mean": latency_p95_mean,
                    "latency_p95_ms_std": latency_p95_std,
                },
                "seeds": sorted({summary.seed_id for summary in summaries}),
            }
        )

    payload = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "input_glob": input_glob,
        "seed_files": [path.as_posix() for path in matrix_paths],
        "groups": groups,
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    _write_csv(output_csv, groups)
    _write_markdown_summaries(groups=groups, results_path=results_path, appendix_path=appendix_path)
    return output_json, output_csv, results_path, appendix_path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Merge day12 seed matrix runs into one aggregate.")
    parser.add_argument(
        "--input-glob",
        default=DEFAULT_INPUT_GLOB,
        help=f"Glob pattern for matrix files (default: {DEFAULT_INPUT_GLOB})",
    )
    parser.add_argument(
        "--output-json",
        default=str(DEFAULT_OUTPUT_JSON),
        help=f"Aggregate JSON output path (default: {DEFAULT_OUTPUT_JSON})",
    )
    parser.add_argument(
        "--output-csv",
        default=str(DEFAULT_OUTPUT_CSV),
        help=f"Aggregate CSV output path (default: {DEFAULT_OUTPUT_CSV})",
    )
    parser.add_argument(
        "--results-output",
        default=str(DEFAULT_RESULTS_MD),
        help=f"Day12 summary markdown output (default: {DEFAULT_RESULTS_MD})",
    )
    parser.add_argument(
        "--appendix-output",
        default=str(DEFAULT_APPENDIX_MD),
        help=f"Day12 appendix markdown output (default: {DEFAULT_APPENDIX_MD})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    output_json, output_csv, results_md, appendix_md = merge_day12_seeds(
        input_glob=args.input_glob,
        output_json=Path(args.output_json),
        output_csv=Path(args.output_csv),
        results_path=Path(args.results_output),
        appendix_path=Path(args.appendix_output),
    )
    print(f"Wrote day12 aggregate json: {output_json}")
    print(f"Wrote day12 aggregate csv: {output_csv}")
    print(f"Wrote day12 summary: {results_md}")
    print(f"Wrote day12 appendix: {appendix_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
