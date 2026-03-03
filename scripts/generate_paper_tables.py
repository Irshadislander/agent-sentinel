from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_INPUT_PATH = Path("bench/results/matrix.json")
DEFAULT_AGGREGATE_PATH = Path("bench/results/day12_aggregate.json")
DEFAULT_RESULTS_DAY11_PATH = Path("paper/RESULTS_DAY11.md")
DEFAULT_APPENDIX_DAY11_PATH = Path("paper/APPENDIX_DAY11.md")
DEFAULT_RESULTS_DAY12_PATH = Path("paper/RESULTS_DAY12.md")
DEFAULT_APPENDIX_DAY12_PATH = Path("paper/APPENDIX_DAY12.md")
DEFAULT_OUTPUT_DAY11_PATH = Path("paper/results_tables.md")
DEFAULT_OUTPUT_DAY12_PATH = Path("paper/results_tables_day12.md")
UER_DENIED_CATEGORIES = {"malicious", "policy_blocked"}


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


def _load_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("input payload must be a JSON object")
    return payload


def _load_rows_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    grouped_payload = payload.get("grouped")
    if isinstance(grouped_payload, dict):
        rows: list[dict[str, Any]] = []
        for baseline, scenario_map in sorted(grouped_payload.items()):
            if not isinstance(scenario_map, dict):
                continue
            for scenario_id, items in sorted(scenario_map.items()):
                if not isinstance(items, list):
                    continue
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    normalized = dict(item)
                    normalized.setdefault("baseline", str(baseline))
                    normalized.setdefault("scenario_id", str(scenario_id))
                    rows.append(normalized)
        if rows:
            return rows

    rows_payload = payload.get("rows")
    if isinstance(rows_payload, list):
        return [row for row in rows_payload if isinstance(row, dict)]
    return []


def _load_aggregate_groups_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    groups = payload.get("groups") if isinstance(payload, dict) else None
    if not isinstance(groups, list):
        return []
    return [group for group in groups if isinstance(group, dict)]


def _group_by_baseline(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        baseline = str(row.get("baseline", "")).strip() or "unknown"
        grouped.setdefault(baseline, []).append(row)
    return grouped


def _group_by_scenario(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        scenario_id = str(row.get("scenario_id", "")).strip() or "default"
        grouped.setdefault(scenario_id, []).append(row)
    return grouped


def _metrics(rows: list[dict[str, Any]]) -> dict[str, float]:
    total = len(rows)
    if total == 0:
        return {"UER": 0.0, "FAR": 0.0, "TCR": 0.0, "EDS": 0.0}

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

    return {"UER": uer, "FAR": far, "TCR": tcr, "EDS": eds}


def _latency(rows: list[dict[str, Any]]) -> tuple[float, float]:
    values = [float(row.get("duration_ms", 0.0)) for row in rows]
    return _percentile(values, 0.50), _percentile(values, 0.95)


def _plugin_count(rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    return max(int(row.get("plugin_entrypoint_count", 0)) for row in rows)


def _default_baseline_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    default_rows = [row for row in rows if str(row.get("baseline", "")) == "default"]
    return default_rows if default_rows else rows


def _table_baseline_metrics(grouped: dict[str, list[dict[str, Any]]]) -> list[str]:
    default_metrics = _metrics(grouped.get("default", []))
    default_plugin_count = _plugin_count(grouped.get("default", []))
    lines = [
        "## Table 1: Baseline Metrics",
        "",
        "| Baseline | UER | ΔUER vs default | FAR | ΔFAR vs default | TCR | ΔTCR vs default | EDS | ΔEDS vs default | plugin_loads | Δplugin_loads vs default |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for baseline in sorted(grouped):
        values = _metrics(grouped[baseline])
        plugin_count = _plugin_count(grouped[baseline])
        lines.append(
            "| "
            + " | ".join(
                [
                    baseline,
                    f"{values['UER']:.4f}",
                    f"{values['UER'] - default_metrics['UER']:+.4f}",
                    f"{values['FAR']:.4f}",
                    f"{values['FAR'] - default_metrics['FAR']:+.4f}",
                    f"{values['TCR']:.4f}",
                    f"{values['TCR'] - default_metrics['TCR']:+.4f}",
                    f"{values['EDS']:.4f}",
                    f"{values['EDS'] - default_metrics['EDS']:+.4f}",
                    str(plugin_count),
                    f"{plugin_count - default_plugin_count:+d}",
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _table_scale_stability(rows: list[dict[str, Any]]) -> list[str]:
    scenario_rows = _group_by_scenario(_default_baseline_rows(rows))
    scale_items: list[tuple[int, str, list[dict[str, Any]]]] = []
    for scenario_id, items in scenario_rows.items():
        match = re.fullmatch(r"scale_n(\d+)", scenario_id)
        if match:
            scale_items.append((int(match.group(1)), scenario_id, items))

    lines = [
        "## Table A: Scale Stability",
        "",
        "| scenario_id | N | UER | FAR | TCR | EDS | p50_ms | p95_ms |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for n_value, scenario_id, items in sorted(scale_items, key=lambda item: item[0]):
        metrics = _metrics(items)
        p50, p95 = _latency(items)
        lines.append(
            f"| {scenario_id} | {n_value} | {metrics['UER']:.4f} | {metrics['FAR']:.4f} | "
            f"{metrics['TCR']:.4f} | {metrics['EDS']:.4f} | {p50:.3f} | {p95:.3f} |"
        )

    if len(lines) == 4:
        lines.append("| - | - | - | - | - | - | - | - |")
    lines.append("")
    return lines


def _table_stress_degradation(rows: list[dict[str, Any]]) -> list[str]:
    scenario_rows = _group_by_scenario(_default_baseline_rows(rows))
    default_rows = scenario_rows.get("default", [])
    default_metrics = _metrics(default_rows)
    default_p50, default_p95 = _latency(default_rows)

    stress_items: list[tuple[float, float, str, list[dict[str, Any]]]] = []
    for scenario_id, items in scenario_rows.items():
        match = re.fullmatch(r"stress_m([0-9.]+)_p([0-9.]+)", scenario_id)
        if match:
            stress_items.append((float(match.group(1)), float(match.group(2)), scenario_id, items))

    lines = [
        "## Table B: Stress Degradation",
        "",
        "| scenario_id | malformed_p | plugin_p | ΔUER | ΔFAR | ΔTCR | ΔEDS | Δp50_ms | Δp95_ms |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for malformed_p, plugin_p, scenario_id, items in sorted(stress_items):
        metrics = _metrics(items)
        p50, p95 = _latency(items)
        lines.append(
            f"| {scenario_id} | {malformed_p:.2f} | {plugin_p:.2f} | "
            f"{metrics['UER'] - default_metrics['UER']:+.4f} | "
            f"{metrics['FAR'] - default_metrics['FAR']:+.4f} | "
            f"{metrics['TCR'] - default_metrics['TCR']:+.4f} | "
            f"{metrics['EDS'] - default_metrics['EDS']:+.4f} | "
            f"{p50 - default_p50:+.3f} | {p95 - default_p95:+.3f} |"
        )

    if len(lines) == 4:
        lines.append("| - | - | - | - | - | - | - | - | - |")
    lines.append("")
    return lines


def _table_sensitivity(rows: list[dict[str, Any]]) -> list[str]:
    scenario_rows = _group_by_scenario(_default_baseline_rows(rows))
    sensitivity_items: list[tuple[str, list[dict[str, Any]]]] = []
    for scenario_id, items in scenario_rows.items():
        if scenario_id.startswith("sens_"):
            sensitivity_items.append((scenario_id, items))

    lines = [
        "## Table C: Sensitivity",
        "",
        "| scenario_id | strictness | trace_sample_rate | allowlist_size | UER | FAR | TCR | EDS | p50_ms | p95_ms |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for scenario_id, items in sorted(sensitivity_items):
        metrics = _metrics(items)
        p50, p95 = _latency(items)
        strictness = str(items[0].get("policy_strictness", "medium")) if items else "medium"
        sample_rate = float(items[0].get("trace_sample_rate", 1.0)) if items else 1.0
        allowlist_size = int(items[0].get("allowlist_size", -1)) if items else -1
        lines.append(
            f"| {scenario_id} | {strictness} | {sample_rate:.2f} | {allowlist_size} | "
            f"{metrics['UER']:.4f} | {metrics['FAR']:.4f} | {metrics['TCR']:.4f} | "
            f"{metrics['EDS']:.4f} | {p50:.3f} | {p95:.3f} |"
        )

    if len(lines) == 4:
        lines.append("| - | - | - | - | - | - | - | - | - | - |")
    lines.append("")
    return lines


def _table_stability_across_seeds(aggregate_groups: list[dict[str, Any]]) -> list[str]:
    lines = [
        "## Table X: Stability Across Seeds (mean ± std)",
        "",
        "| baseline | scenario_id | UER (mean±std) | FAR (mean±std) | TCR (mean±std) | EDS (mean±std) | plugin_loads (mean±std) | p95 latency ms (mean±std) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for group in sorted(
        aggregate_groups,
        key=lambda item: (str(item.get("baseline", "")), str(item.get("scenario_id", ""))),
    ):
        metrics = group.get("metrics", {})
        if not isinstance(metrics, dict):
            metrics = {}
        lines.append(
            "| "
            + " | ".join(
                [
                    str(group.get("baseline", "unknown")),
                    str(group.get("scenario_id", "default")),
                    f"{float(metrics.get('uer_mean', 0.0)):.4f} ± {float(metrics.get('uer_std', 0.0)):.4f}",
                    f"{float(metrics.get('far_mean', 0.0)):.4f} ± {float(metrics.get('far_std', 0.0)):.4f}",
                    f"{float(metrics.get('tcr_mean', 0.0)):.4f} ± {float(metrics.get('tcr_std', 0.0)):.4f}",
                    f"{float(metrics.get('eds_mean', 0.0)):.4f} ± {float(metrics.get('eds_std', 0.0)):.4f}",
                    f"{float(metrics.get('plugin_loads_mean', 0.0)):.2f} ± {float(metrics.get('plugin_loads_std', 0.0)):.2f}",
                    f"{float(metrics.get('latency_p95_ms_mean', 0.0)):.3f} ± {float(metrics.get('latency_p95_ms_std', 0.0)):.3f}",
                ]
            )
            + " |"
        )

    if len(lines) == 4:
        lines.append("| - | - | - | - | - | - | - | - |")
    lines.append("")
    return lines


def _render_markdown(
    *,
    source: Path,
    rows: list[dict[str, Any]],
    aggregate_groups: list[dict[str, Any]],
) -> str:
    generated_at = datetime.now(UTC).isoformat()

    lines: list[str] = [
        "# Paper Result Tables",
        "",
        f"- Source: `{source.as_posix()}`",
        f"- Generated at (UTC): `{generated_at}`",
        "",
    ]

    if rows:
        baseline_grouped = _group_by_baseline(rows)
        lines.extend(_table_baseline_metrics(baseline_grouped))
        lines.extend(_table_scale_stability(rows))
        lines.extend(_table_stress_degradation(rows))
        lines.extend(_table_sensitivity(rows))

    lines.extend(_table_stability_across_seeds(aggregate_groups))
    return "\n".join(lines)


def _render_results_summary(
    *,
    rows: list[dict[str, Any]],
    aggregate_groups: list[dict[str, Any]],
    day_label: str,
) -> str:
    lines = [
        f"# {day_label} Results Summary",
        "",
        "## Key Findings",
        "",
    ]

    if rows:
        baseline_grouped = _group_by_baseline(rows)
        default_metrics = _metrics(baseline_grouped.get("default", []))
        no_policy_metrics = _metrics(baseline_grouped.get("no_policy", []))
        no_trace_metrics = _metrics(baseline_grouped.get("no_trace", []))
        raw_error_metrics = _metrics(baseline_grouped.get("raw_errors", []))

        lines.extend(
            [
                f"- UER shift (no_policy - default): {no_policy_metrics['UER'] - default_metrics['UER']:+.4f}",
                f"- TCR shift (no_trace - default): {no_trace_metrics['TCR'] - default_metrics['TCR']:+.4f}",
                f"- FAR shift (raw_errors - default): {raw_error_metrics['FAR'] - default_metrics['FAR']:+.4f}",
                "",
            ]
        )

    if aggregate_groups:
        lines.append("## Seed Stability (mean ± std)")
        lines.append("")
        for group in sorted(
            aggregate_groups,
            key=lambda item: (str(item.get("scenario_id", "")), str(item.get("baseline", ""))),
        ):
            metrics = group.get("metrics", {})
            if not isinstance(metrics, dict):
                continue
            lines.append(
                "- "
                f"{group.get('scenario_id', 'default')} / {group.get('baseline', 'unknown')}: "
                f"UER={float(metrics.get('uer_mean', 0.0)):.4f}±{float(metrics.get('uer_std', 0.0)):.4f}, "
                f"FAR={float(metrics.get('far_mean', 0.0)):.4f}±{float(metrics.get('far_std', 0.0)):.4f}, "
                f"TCR={float(metrics.get('tcr_mean', 0.0)):.4f}±{float(metrics.get('tcr_std', 0.0)):.4f}, "
                f"EDS={float(metrics.get('eds_mean', 0.0)):.4f}±{float(metrics.get('eds_std', 0.0)):.4f}"
            )
        lines.append("")

    lines.extend(
        [
            "## Bullet Insights",
            "",
            "- Policy bypass drives the largest unsafe-execution increase in this harness.",
            "- Trace suppression directly reduces forensic completeness.",
            "- Raw exception pathways increase ambiguity relative to structured errors.",
            "- Seed-level aggregation is required for stable comparison claims.",
            "",
        ]
    )
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate markdown tables for paper metrics.")
    parser.add_argument(
        "--input",
        "--matrix-input",
        dest="input_path",
        default=str(DEFAULT_INPUT_PATH),
        help=f"Input JSON path (default: {DEFAULT_INPUT_PATH})",
    )
    parser.add_argument(
        "--aggregate-input",
        default=str(DEFAULT_AGGREGATE_PATH),
        help=f"Optional aggregate JSON path for Table X (default: {DEFAULT_AGGREGATE_PATH})",
    )
    parser.add_argument(
        "--output",
        default="",
        help=(
            "Output markdown path. Default is paper/results_tables.md for matrix input "
            "or paper/results_tables_day12.md for day12 aggregate input."
        ),
    )
    parser.add_argument(
        "--results-output",
        default="",
        help="Optional summary markdown output path.",
    )
    parser.add_argument(
        "--appendix-output",
        default="",
        help="Optional appendix markdown output path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    input_path = Path(args.input_path)
    aggregate_input_path = Path(args.aggregate_input) if args.aggregate_input else None
    if not input_path.exists():
        raise SystemExit(f"input not found: {input_path}")

    payload = _load_payload(input_path)
    rows = _load_rows_from_payload(payload)
    direct_aggregate_groups = _load_aggregate_groups_from_payload(payload)

    is_day12_input = "day12_aggregate" in input_path.name

    aggregate_groups: list[dict[str, Any]] = []
    if direct_aggregate_groups:
        aggregate_groups = direct_aggregate_groups
    elif aggregate_input_path is not None and aggregate_input_path.exists():
        aggregate_groups = _load_aggregate_groups_from_payload(_load_payload(aggregate_input_path))

    output_path = (
        Path(args.output)
        if args.output
        else (DEFAULT_OUTPUT_DAY12_PATH if is_day12_input else DEFAULT_OUTPUT_DAY11_PATH)
    )
    results_output_path = (
        Path(args.results_output)
        if args.results_output
        else (DEFAULT_RESULTS_DAY12_PATH if is_day12_input else DEFAULT_RESULTS_DAY11_PATH)
    )
    appendix_output_path = (
        Path(args.appendix_output)
        if args.appendix_output
        else (DEFAULT_APPENDIX_DAY12_PATH if is_day12_input else DEFAULT_APPENDIX_DAY11_PATH)
    )

    markdown = _render_markdown(source=input_path, rows=rows, aggregate_groups=aggregate_groups)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")

    day_label = "Day 12" if is_day12_input else "Day 11"
    summary_markdown = _render_results_summary(
        rows=rows,
        aggregate_groups=aggregate_groups,
        day_label=day_label,
    )
    results_output_path.parent.mkdir(parents=True, exist_ok=True)
    appendix_output_path.parent.mkdir(parents=True, exist_ok=True)
    results_output_path.write_text(summary_markdown, encoding="utf-8")
    appendix_output_path.write_text(markdown, encoding="utf-8")

    print(f"Wrote paper tables: {output_path}")
    print(f"Wrote summary: {results_output_path}")
    print(f"Wrote appendix: {appendix_output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
