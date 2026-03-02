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

DEFAULT_INPUT_PATH = Path("bench/results/latest.json")
DEFAULT_OUTPUT_PATH = Path("docs/bench_report.md")
DEFAULT_MATRIX_INPUT_PATH = Path("bench/results/matrix.json")


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
            f"| {idx} | {row.mode} | {_safe_cell(row.task_name)} | {row.latency_ms:.3f} | {row.exit_code} |"
        )

    if matrix_rows:
        lines.extend(
            [
                "",
                "## Matrix Comparison",
                "",
                "| mode_label | avg_runtime_ms | failure_count | trace_event_count | exit_code_histogram |",
                "|---|---:|---:|---:|---|",
            ]
        )
        for row in sorted(matrix_rows, key=lambda item: str(item.get("mode_label", ""))):
            histogram = row.get("exit_code_histogram", {})
            histogram_text = json.dumps(histogram, sort_keys=True, separators=(",", ":"))
            lines.append(
                "| "
                + " | ".join(
                    [
                        _safe_cell(row.get("mode_label", "n/a")),
                        _safe_cell(row.get("avg_runtime_ms", "n/a")),
                        _safe_cell(row.get("failure_count", "n/a")),
                        _safe_cell(row.get("trace_event_count", "n/a")),
                        _safe_cell(histogram_text),
                    ]
                )
                + " |"
            )

    lines.append("")
    return "\n".join(lines)


def _load_matrix_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return []
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
