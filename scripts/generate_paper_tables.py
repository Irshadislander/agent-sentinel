from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_MATRIX_PATH = Path("bench/results/matrix.json")
DEFAULT_OUTPUT_PATH = Path("paper/results_tables.md")


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


def _load_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("matrix payload must be a JSON object")
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise ValueError("matrix payload missing list field 'rows'")
    filtered = [row for row in rows if isinstance(row, dict)]
    if not filtered:
        raise ValueError("matrix payload contains no usable rows")
    return filtered


def _group_by_baseline(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        baseline = str(row.get("baseline", "")).strip() or "unknown"
        grouped.setdefault(baseline, []).append(row)
    return grouped


def _metrics(rows: list[dict[str, Any]]) -> dict[str, float]:
    total = len(rows)
    if total == 0:
        return {"UER": 0.0, "FAR": 0.0, "TCR": 0.0, "EDS": 0.0}

    denied_expected = [row for row in rows if str(row.get("category", "")) != "benign"]
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


def _render_markdown(*, source: Path, grouped: dict[str, list[dict[str, Any]]]) -> str:
    generated_at = datetime.now(UTC).isoformat()
    lines: list[str] = [
        "# Paper Result Tables",
        "",
        f"- Source: `{source.as_posix()}`",
        f"- Generated at (UTC): `{generated_at}`",
        "",
        "## Table 1: Baseline Metrics",
        "",
        "| Baseline | UER | FAR | TCR | EDS |",
        "|---|---:|---:|---:|---:|",
    ]

    for baseline in sorted(grouped):
        values = _metrics(grouped[baseline])
        lines.append(
            "| "
            + " | ".join(
                [
                    baseline,
                    f"{values['UER']:.4f}",
                    f"{values['FAR']:.4f}",
                    f"{values['TCR']:.4f}",
                    f"{values['EDS']:.4f}",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Table 2: Latency",
            "",
            "| Baseline | p50 (ms) | p95 (ms) |",
            "|---|---:|---:|",
        ]
    )

    for baseline in sorted(grouped):
        latencies = [float(row.get("duration_ms", 0.0)) for row in grouped[baseline]]
        lines.append(
            f"| {baseline} | {_percentile(latencies, 0.50):.3f} | {_percentile(latencies, 0.95):.3f} |"
        )

    lines.append("")
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate markdown tables for paper metrics.")
    parser.add_argument(
        "--matrix-input",
        default=str(DEFAULT_MATRIX_PATH),
        help=f"Matrix input JSON path (default: {DEFAULT_MATRIX_PATH})",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help=f"Output markdown path (default: {DEFAULT_OUTPUT_PATH})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    matrix_path = Path(args.matrix_input)
    output_path = Path(args.output)

    if not matrix_path.exists():
        raise SystemExit(f"matrix input not found: {matrix_path}")

    rows = _load_rows(matrix_path)
    grouped = _group_by_baseline(rows)
    markdown = _render_markdown(source=matrix_path, grouped=grouped)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    print(f"Wrote paper tables: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
