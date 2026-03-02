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
    source_path: Path,
    generated_at: str,
    git_sha: str,
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
        f"- Source: `{source_path.as_posix()}`",
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

    lines.append("")
    return "\n".join(lines)


def generate_report(
    *,
    input_path: Path = DEFAULT_INPUT_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    generated_at: str | None = None,
    git_sha: str | None = None,
) -> Path:
    report = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(report, dict):
        raise ValueError("benchmark report JSON must be an object")

    markdown = _render_markdown(
        report,
        source_path=input_path,
        generated_at=generated_at or _utc_now_iso(),
        git_sha=git_sha or _detect_git_sha(),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    return output_path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate markdown benchmark summary.")
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT_PATH),
        help=f"Input benchmark JSON path (default: {DEFAULT_INPUT_PATH}).",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help=f"Output markdown path (default: {DEFAULT_OUTPUT_PATH}).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    output = generate_report(input_path=Path(args.input), output_path=Path(args.output))
    print(f"Benchmark markdown report written: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
