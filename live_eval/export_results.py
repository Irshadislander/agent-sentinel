from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import OrderedDict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_RESULTS_PATH = Path(__file__).resolve().parent / "results" / "live_results.json"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "results"


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])

    index = (len(ordered) - 1) * p
    low = int(index)
    high = min(low + 1, len(ordered) - 1)
    weight = index - low
    return ordered[low] + (ordered[high] - ordered[low]) * weight


def _coerce_results(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        results = payload.get("results", [])
        if isinstance(results, list):
            return [row for row in results if isinstance(row, dict)]
    raise ValueError("live_results.json must contain a list of task records")


def _load_results(path: Path) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return _coerce_results(raw)


def _category_summary(rows: list[dict[str, Any]], category: str) -> dict[str, Any]:
    subset = [row for row in rows if str(row.get("category", "")) == category]
    latencies = [float(row.get("latency_ms", 0.0)) for row in subset]
    total = len(subset)
    success = sum(1 for row in subset if bool(row.get("success")))
    blocked = sum(1 for row in subset if bool(row.get("blocked")))
    actual_allow = sum(1 for row in subset if str(row.get("actual_outcome", "")) == "ALLOW")
    actual_deny = sum(1 for row in subset if str(row.get("actual_outcome", "")) == "DENY")
    execution_errors = sum(1 for row in subset if str(row.get("execution_error", "")).strip())
    return {
        "category": category,
        "total": total,
        "success": success,
        "blocked": blocked,
        "allow": actual_allow,
        "deny": actual_deny,
        "execution_errors": execution_errors,
        "success_rate": round(success / total, 4) if total else 0.0,
        "blocked_rate": round(blocked / total, 4) if total else 0.0,
        "median_latency_ms": round(statistics.median(latencies), 3) if latencies else 0.0,
        "p95_latency_ms": round(_percentile(latencies, 0.95), 3) if latencies else 0.0,
    }


def build_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    categories = list(
        OrderedDict.fromkeys(str(row.get("category", "")) for row in rows if row.get("category"))
    )
    total_tasks = len(rows)
    benign = [row for row in rows if str(row.get("type", "")) == "benign"]
    attack = [row for row in rows if str(row.get("type", "")) == "attack"]
    robustness = [row for row in rows if str(row.get("type", "")) == "robustness"]
    latencies = [float(row.get("latency_ms", 0.0)) for row in rows]

    benign_allowed_rate = (
        sum(1 for row in benign if str(row.get("actual_outcome", "")) == "ALLOW") / len(benign)
        if benign
        else 0.0
    )
    unsafe_blocked_rate = (
        sum(1 for row in attack if str(row.get("actual_outcome", "")) == "DENY") / len(attack)
        if attack
        else 0.0
    )
    robustness_handled_rate = (
        sum(
            1
            for row in robustness
            if str(row.get("actual_outcome", "")) == str(row.get("expected_outcome", ""))
        )
        / len(robustness)
        if robustness
        else 0.0
    )

    summary = {
        "generated_at": _utc_now(),
        "total_tasks": total_tasks,
        "total_benign_tasks": len(benign),
        "total_attack_tasks": len(attack),
        "total_robustness_tasks": len(robustness),
        "benign_allowed_rate": round(benign_allowed_rate, 4),
        "benign_preservation_rate": round(benign_allowed_rate, 4),
        "unsafe_blocked_rate": round(unsafe_blocked_rate, 4),
        "attack_blocking_rate": round(unsafe_blocked_rate, 4),
        "robustness_handled_rate": round(robustness_handled_rate, 4),
        "median_latency_ms": round(statistics.median(latencies), 3) if latencies else 0.0,
        "p95_latency_ms": round(_percentile(latencies, 0.95), 3) if latencies else 0.0,
        "execution_error_count": sum(
            1 for row in rows if str(row.get("execution_error", "")).strip()
        ),
        "by_category": [_category_summary(rows, category) for category in categories],
    }
    return summary


def _safe_cell(value: Any) -> str:
    return str(value).replace("|", "\\|")


def render_summary_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Live Evaluation Summary",
        "",
        f"- Generated at: `{summary.get('generated_at', '')}`",
        f"- Total tasks: `{summary.get('total_tasks', 0)}`",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Total benign tasks | `{summary.get('total_benign_tasks', 0)}` |",
        f"| Total attack tasks | `{summary.get('total_attack_tasks', 0)}` |",
        f"| Total robustness tasks | `{summary.get('total_robustness_tasks', 0)}` |",
        f"| Benign preservation rate | `{summary.get('benign_preservation_rate', 0.0) * 100:.1f}%` |",
        f"| Attack blocking rate | `{summary.get('attack_blocking_rate', 0.0) * 100:.1f}%` |",
        f"| Robustness handled rate | `{summary.get('robustness_handled_rate', 0.0) * 100:.1f}%` |",
        f"| Median latency | `{summary.get('median_latency_ms', 0.0):.3f} ms` |",
        f"| P95 latency | `{summary.get('p95_latency_ms', 0.0):.3f} ms` |",
        "",
        "## Breakdown By Category",
        "",
        "| category | total | success | blocked | allow | deny | execution_errors | success_rate | median_latency_ms | p95_latency_ms |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary.get("by_category", []):
        if not isinstance(row, dict):
            continue
        lines.append(
            "| "
            + " | ".join(
                [
                    _safe_cell(row.get("category", "")),
                    _safe_cell(row.get("total", 0)),
                    _safe_cell(row.get("success", 0)),
                    _safe_cell(row.get("blocked", 0)),
                    _safe_cell(row.get("allow", 0)),
                    _safe_cell(row.get("deny", 0)),
                    _safe_cell(row.get("execution_errors", 0)),
                    f"{float(row.get('success_rate', 0.0)) * 100:.1f}%",
                    f"{float(row.get('median_latency_ms', 0.0)):.3f}",
                    f"{float(row.get('p95_latency_ms', 0.0)):.3f}",
                ]
            )
            + " |"
        )

    return "\n".join(lines) + "\n"


def _write_csv(results: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "run_id",
        "timestamp",
        "model_name",
        "task_id",
        "type",
        "category",
        "expected_outcome",
        "actual_outcome",
        "blocked",
        "success",
        "tool_name",
        "tool_latency_ms",
        "latency_ms",
        "args",
        "denial_reason",
        "execution_error",
        "prompt",
        "final_answer",
        "tool_calls",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            serialized = dict(row)
            serialized["args"] = json.dumps(
                serialized.get("args", {}), ensure_ascii=False, sort_keys=True
            )
            serialized["tool_calls"] = json.dumps(
                serialized.get("tool_calls", []), ensure_ascii=False, sort_keys=True
            )
            writer.writerow({field: serialized.get(field, "") for field in fieldnames})


def export_results(
    *,
    results_path: Path | str = DEFAULT_RESULTS_PATH,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    results_path = Path(results_path)
    output_dir = Path(output_dir)
    results = _load_results(results_path)
    summary = build_summary(results)

    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "live_summary.json"
    markdown_path = output_dir / "live_summary_table.md"

    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(render_summary_markdown(summary), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export live evaluation summary artifacts.")
    parser.add_argument(
        "--results",
        type=Path,
        default=DEFAULT_RESULTS_PATH,
        help="Path to live_results.json.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where summary artifacts should be written.",
    )
    args = parser.parse_args(argv)

    summary = export_results(results_path=args.results, output_dir=args.output_dir)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
