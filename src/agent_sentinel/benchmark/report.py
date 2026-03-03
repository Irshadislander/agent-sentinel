from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agent_sentinel.cli_exit_codes import DENIED, INTERNAL_ERROR, OK

DEFAULT_INPUT_PATH = Path("artifacts/bench/latest.json")
DEFAULT_OUTPUT_PATH = Path("docs/bench_report.md")
DEFAULT_MATRIX_INPUT_PATH = Path("artifacts/bench/matrix.json")
UER_DENIED_CATEGORIES = {"malicious", "policy_blocked"}


@dataclass(frozen=True)
class TaskRow:
    mode: str
    task_name: str
    category: str
    success: bool
    blocked: bool
    latency_ms: float
    exit_code: int
    error: str


def _utc_now_iso() -> str:
    now = datetime.now(UTC).replace(microsecond=0)
    return now.isoformat().replace("+00:00", "Z")


def _detect_git_sha() -> str:
    env_sha = os.getenv("GITHUB_SHA")
    if env_sha:
        return env_sha[:12]

    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=True,
            text=True,
            capture_output=True,
        )
    except Exception:
        return "unknown"
    return completed.stdout.strip() or "unknown"


def _derive_exit_code(*, success: bool, blocked: bool) -> int:
    if success:
        return OK
    if blocked:
        return DENIED
    return INTERNAL_ERROR


def _safe_cell(value: object) -> str:
    return str(value).replace("|", "\\|")


def _collect_task_rows(report: dict[str, Any]) -> list[TaskRow]:
    rows: list[TaskRow] = []
    for mode in ("baseline", "secured"):
        mode_payload = report.get(mode, {})
        if not isinstance(mode_payload, dict):
            continue
        results = mode_payload.get("results", [])
        if not isinstance(results, list):
            continue
        for result in results:
            if not isinstance(result, dict):
                continue
            success = bool(result.get("success", False))
            blocked = bool(result.get("blocked", False))
            latency_ms = float(result.get("latency_ms", 0.0))
            rows.append(
                TaskRow(
                    mode=mode,
                    task_name=str(result.get("task_name", "")),
                    category=str(result.get("category", "")),
                    success=success,
                    blocked=blocked,
                    latency_ms=latency_ms,
                    exit_code=_derive_exit_code(success=success, blocked=blocked),
                    error=str(result.get("error", "")),
                )
            )
    return rows


def _exit_code_histogram(rows: list[TaskRow]) -> dict[int, int]:
    histogram: dict[int, int] = {}
    for row in rows:
        histogram[row.exit_code] = histogram.get(row.exit_code, 0) + 1
    return dict(sorted(histogram.items()))


def _top_slowest(rows: list[TaskRow], limit: int = 5) -> list[TaskRow]:
    ranked = sorted(rows, key=lambda row: (-row.latency_ms, row.mode, row.task_name))
    return ranked[:limit]


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


def _matrix_groups(matrix_rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in matrix_rows:
        baseline = str(row.get("baseline", "")).strip() or "unknown"
        grouped.setdefault(baseline, []).append(row)
    return grouped


def _table1_metrics(rows: list[dict[str, Any]]) -> dict[str, float]:
    total = len(rows)
    if total == 0:
        return {"UER": 0.0, "FAR": 0.0, "TCR": 0.0, "EDS": 0.0, "PEA": 0.0}

    denied_expected = [
        row for row in rows if str(row.get("category", "")).strip() in UER_DENIED_CATEGORIES
    ]
    denied_but_executed = sum(1 for row in denied_expected if row.get("decision") == "allow")
    uer = denied_but_executed / len(denied_expected) if denied_expected else 0.0

    failures = [row for row in rows if int(row.get("exit_code", 0)) != OK]
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

    correct = 0
    for row in rows:
        expected = "allow" if str(row.get("category", "")) == "benign" else "deny"
        if str(row.get("decision", "")) == expected:
            correct += 1
    pea = correct / total

    return {"UER": uer, "FAR": far, "TCR": tcr, "EDS": eds, "PEA": pea}


def _reason_code_for_row(row: dict[str, Any]) -> str:
    explicit = str(row.get("reason_code", "")).strip()
    if explicit:
        return explicit

    error_kind = str(row.get("error_kind", "")).strip()
    if error_kind and error_kind not in {"none", "unknown"}:
        return error_kind.upper()

    return "UNKNOWN_REASON"


def _denial_reason_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        if str(row.get("decision", "")).strip() != "deny":
            continue
        reason_code = _reason_code_for_row(row)
        counts[reason_code] = counts.get(reason_code, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _top_reason_codes_by_category(
    rows: list[dict[str, Any]],
    *,
    limit: int = 3,
) -> dict[str, list[tuple[str, int]]]:
    category_counts: dict[str, dict[str, int]] = {}
    for row in rows:
        if str(row.get("decision", "")).strip() != "deny":
            continue
        category = str(row.get("category", "")).strip() or "unknown"
        reason_code = _reason_code_for_row(row)
        reason_counts = category_counts.setdefault(category, {})
        reason_counts[reason_code] = reason_counts.get(reason_code, 0) + 1

    ranked: dict[str, list[tuple[str, int]]] = {}
    for category, reason_counts in category_counts.items():
        top = sorted(reason_counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
        ranked[category] = top
    return ranked


def _denied_but_executed_count(rows: list[dict[str, Any]]) -> int:
    denied_expected = [
        row for row in rows if str(row.get("category", "")).strip() in UER_DENIED_CATEGORIES
    ]
    return sum(1 for row in denied_expected if str(row.get("decision", "")).strip() == "allow")


def _render_markdown(
    report: dict[str, Any],
    *,
    source_label: str,
    generated_at: str,
    git_sha: str,
    matrix_rows: list[dict[str, Any]] | None = None,
) -> str:
    benchmark_id = str(report.get("benchmark_id", "unknown"))
    tasks_total = int(report.get("tasks_total", 0))
    rows = _collect_task_rows(report)
    histogram = _exit_code_histogram(rows)
    slowest = _top_slowest(rows, limit=5)

    lines: list[str] = [
        "# Benchmark Report",
        "",
        f"- Generated at: `{generated_at}`",
        f"- Git SHA: `{git_sha}`",
        f"- Source: `{source_label}`",
        f"- Benchmark ID: `{benchmark_id}`",
        f"- Tasks total: `{tasks_total}`",
        "",
        "## Mode Metrics",
        "",
        "| mode | task_success | attack_success | false_blocks | latency_ms |",
        "|---|---:|---:|---:|---:|",
    ]

    for mode in ("baseline", "secured"):
        mode_payload = report.get(mode, {})
        metrics = mode_payload.get("metrics", {}) if isinstance(mode_payload, dict) else {}
        if not isinstance(metrics, dict):
            metrics = {}
        lines.append(
            "| "
            + " | ".join(
                [
                    mode,
                    _safe_cell(metrics.get("task_success", "n/a")),
                    _safe_cell(metrics.get("attack_success", "n/a")),
                    _safe_cell(metrics.get("false_blocks", "n/a")),
                    _safe_cell(metrics.get("latency", "n/a")),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Per-task Outcomes",
            "",
            "| mode | task_name | category | success | blocked | latency_ms | exit_code | error |",
            "|---|---|---|---:|---:|---:|---:|---|",
        ]
    )

    for row in sorted(rows, key=lambda item: (item.mode, item.task_name)):
        lines.append(
            "| "
            + " | ".join(
                [
                    row.mode,
                    _safe_cell(row.task_name),
                    _safe_cell(row.category),
                    "yes" if row.success else "no",
                    "yes" if row.blocked else "no",
                    f"{row.latency_ms:.3f}",
                    str(row.exit_code),
                    _safe_cell(row.error),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Exit Code Histogram",
            "",
            "| exit_code | count |",
            "|---:|---:|",
        ]
    )
    for code, count in histogram.items():
        lines.append(f"| {code} | {count} |")

    lines.extend(
        [
            "",
            "## Top 5 Slowest Tasks",
            "",
            "| rank | mode | task_name | latency_ms | exit_code |",
            "|---:|---|---|---:|---:|",
        ]
    )
    for idx, row in enumerate(slowest, start=1):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(idx),
                    row.mode,
                    _safe_cell(row.task_name),
                    f"{row.latency_ms:.3f}",
                    str(row.exit_code),
                ]
            )
            + " |"
        )

    if matrix_rows:
        groups = _matrix_groups(matrix_rows)

        lines.extend(
            [
                "",
                "## Table 1: Default vs Baselines (Per-Metric)",
                "",
                "| baseline | UER | FAR | TCR | EDS | PEA |",
                "|---|---:|---:|---:|---:|---:|",
            ]
        )
        for baseline in sorted(groups):
            metrics = _table1_metrics(groups[baseline])
            lines.append(
                "| "
                + " | ".join(
                    [
                        baseline,
                        f"{metrics['UER']:.4f}",
                        f"{metrics['FAR']:.4f}",
                        f"{metrics['TCR']:.4f}",
                        f"{metrics['EDS']:.4f}",
                        f"{metrics['PEA']:.4f}",
                    ]
                )
                + " |"
            )

        lines.extend(
            [
                "",
                "## Table 2: Per-Category Breakdown",
                "",
                "| baseline | category | count | allow_rate | deny_rate |",
                "|---|---|---:|---:|---:|",
            ]
        )
        for baseline in sorted(groups):
            rows_for_baseline = groups[baseline]
            categories = sorted({str(row.get("category", "")) for row in rows_for_baseline})
            for category in categories:
                category_rows = [
                    row for row in rows_for_baseline if str(row.get("category", "")) == category
                ]
                count = len(category_rows)
                allow_rate = (
                    sum(1 for row in category_rows if str(row.get("decision", "")) == "allow")
                    / count
                    if count
                    else 0.0
                )
                deny_rate = (
                    sum(1 for row in category_rows if str(row.get("decision", "")) == "deny")
                    / count
                    if count
                    else 0.0
                )
                lines.append(
                    f"| {baseline} | {category} | {count} | {allow_rate:.4f} | {deny_rate:.4f} |"
                )

        lines.extend(
            [
                "",
                "## Table 3: Latency p50/p95",
                "",
                "| baseline | scope | p50_ms | p95_ms |",
                "|---|---|---:|---:|",
            ]
        )
        for baseline in sorted(groups):
            rows_for_baseline = groups[baseline]
            overall = [float(row.get("duration_ms", 0.0)) for row in rows_for_baseline]
            lines.append(
                f"| {baseline} | overall | "
                f"{_percentile(overall, 0.50):.3f} | {_percentile(overall, 0.95):.3f} |"
            )
            categories = sorted({str(row.get("category", "")) for row in rows_for_baseline})
            for category in categories:
                scoped = [
                    float(row.get("duration_ms", 0.0))
                    for row in rows_for_baseline
                    if str(row.get("category", "")) == category
                ]
                lines.append(
                    f"| {baseline} | {category} | "
                    f"{_percentile(scoped, 0.50):.3f} | {_percentile(scoped, 0.95):.3f} |"
                )

        denial_counts = _denial_reason_counts(matrix_rows)
        top_by_category = _top_reason_codes_by_category(matrix_rows)
        denied_but_executed = _denied_but_executed_count(matrix_rows)

        lines.extend(
            [
                "",
                "## Robustness: Denial Reason Codes",
                "",
                f"- Denied-but-executed (critical): `{denied_but_executed}`",
                "",
                "| reason_code | denials |",
                "|---|---:|",
            ]
        )
        if denial_counts:
            for reason_code, count in denial_counts.items():
                lines.append(f"| {reason_code} | {count} |")
        else:
            lines.append("| - | 0 |")

        lines.extend(
            [
                "",
                "## Robustness: Top Reason Codes by Category",
                "",
                "| category | rank | reason_code | denials |",
                "|---|---:|---|---:|",
            ]
        )
        if top_by_category:
            for category in sorted(top_by_category):
                for rank, (reason_code, count) in enumerate(top_by_category[category], start=1):
                    lines.append(f"| {category} | {rank} | {reason_code} | {count} |")
        else:
            lines.append("| - | 1 | - | 0 |")

    lines.append("")
    return "\n".join(lines)


def _load_matrix_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return []

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

    baselines_payload = payload.get("baselines")
    if isinstance(baselines_payload, dict):
        rows: list[dict[str, Any]] = []
        for baseline, items in sorted(baselines_payload.items()):
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                normalized = dict(item)
                normalized.setdefault("baseline", str(baseline))
                rows.append(normalized)
        if rows:
            return rows

    rows_payload = payload.get("rows")
    if isinstance(rows_payload, list):
        rows = [row for row in rows_payload if isinstance(row, dict)]
        return rows
    runs = payload.get("runs", [])
    if not isinstance(runs, list):
        return []
    rows: list[dict[str, Any]] = []
    for run in runs:
        if isinstance(run, dict):
            rows.append(run)
    return rows


def _empty_latest_report() -> dict[str, Any]:
    return {
        "benchmark_id": "matrix-only",
        "tasks_total": 0,
        "baseline": {"metrics": {}, "results": []},
        "secured": {"metrics": {}, "results": []},
    }


def generate_report(
    *,
    input_path: Path | None = DEFAULT_INPUT_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    matrix_input_path: Path | None = DEFAULT_MATRIX_INPUT_PATH,
    generated_at: str | None = None,
    git_sha: str | None = None,
) -> Path:
    source_label = "none"
    report: dict[str, Any]
    if input_path is not None and input_path.exists():
        report = json.loads(input_path.read_text(encoding="utf-8"))
        if not isinstance(report, dict):
            raise ValueError("benchmark report JSON must be an object")
        source_label = input_path.as_posix()
    else:
        report = _empty_latest_report()
        if matrix_input_path is not None:
            source_label = matrix_input_path.as_posix()

    matrix_rows = _load_matrix_rows(matrix_input_path) if matrix_input_path else []
    markdown = _render_markdown(
        report,
        source_label=source_label,
        generated_at=generated_at or _utc_now_iso(),
        git_sha=git_sha or _detect_git_sha(),
        matrix_rows=matrix_rows,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    return output_path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate markdown benchmark summary.")
    parser.add_argument(
        "--input",
        default="",
        help=f"Optional input benchmark JSON path (default: {DEFAULT_INPUT_PATH} if present).",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help=f"Output markdown path (default: {DEFAULT_OUTPUT_PATH}).",
    )
    parser.add_argument(
        "--matrix-input",
        default=str(DEFAULT_MATRIX_INPUT_PATH),
        help=f"Optional matrix benchmark JSON path (default: {DEFAULT_MATRIX_INPUT_PATH}).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    input_path: Path | None
    if args.input:
        input_path = Path(args.input)
    elif DEFAULT_INPUT_PATH.exists():
        input_path = DEFAULT_INPUT_PATH
    else:
        input_path = None
    output = generate_report(
        input_path=input_path,
        output_path=Path(args.output),
        matrix_input_path=Path(args.matrix_input) if args.matrix_input else None,
    )
    print(f"Benchmark markdown report written: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
