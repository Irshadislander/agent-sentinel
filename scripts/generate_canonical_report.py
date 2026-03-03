from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Make `src/` importable when running as a script (subprocess/CI/local).
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from agent_sentinel.benchmark.policy_engine_perf import (  # noqa: E402
    run_policy_engine_benchmark,
    write_policy_engine_benchmark_outputs,
)

BASELINE_ORDER = ["no_policy", "no_trace", "raw_errors", "no_plugin_isolation", "default"]
ATTACK_CATEGORIES = {
    "malicious",
    "policy_blocked",
    "malformed_payload",
    "plugin_failure",
    "trace_stress",
}


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_matrix(matrix_path: Path) -> dict[str, Any]:
    payload = json.loads(matrix_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("matrix payload must be a JSON object")
    return payload


def _matrix_rows(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    rows_payload = matrix.get("rows")
    if isinstance(rows_payload, list):
        return [row for row in rows_payload if isinstance(row, dict)]

    grouped_payload = matrix.get("grouped")
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
        return rows

    return []


def _ordered_baselines(rows: list[dict[str, Any]]) -> list[str]:
    discovered: set[str] = set()
    for row in rows:
        baseline = row.get("baseline")
        if isinstance(baseline, str) and baseline:
            discovered.add(baseline)

    if not discovered:
        return ["placeholder"]

    ordered = [baseline for baseline in BASELINE_ORDER if baseline in discovered]
    ordered.extend(sorted(discovered.difference(BASELINE_ORDER)))
    return ordered


def _percent(value: float) -> float:
    return round(value * 100.0, 2)


def _reason_code(row: dict[str, Any]) -> str:
    reason = str(row.get("reason_code", "")).strip()
    if reason:
        return reason
    error_kind = str(row.get("error_kind", "")).strip()
    if error_kind and error_kind.lower() not in {"none", "unknown"}:
        return error_kind.upper()
    return "UNKNOWN_REASON"


def _baseline_groups(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        baseline = str(row.get("baseline", "")).strip() or "placeholder"
        grouped.setdefault(baseline, []).append(row)
    return grouped


def _policy_decision_errors(rows: list[dict[str, Any]]) -> tuple[int, int]:
    expected_deny_allowed = 0
    expected_allow_denied = 0
    for row in rows:
        category = str(row.get("category", "")).strip()
        decision = str(row.get("decision", "")).strip()
        expected = "allow" if category == "benign" else "deny"
        if expected == "deny" and decision == "allow":
            expected_deny_allowed += 1
        if expected == "allow" and decision == "deny":
            expected_allow_denied += 1
    return expected_deny_allowed, expected_allow_denied


def _trace_completeness(rows: list[dict[str, Any]]) -> float:
    if not rows:
        return 0.0
    traced = sum(1 for row in rows if bool(row.get("has_trace")))
    return _percent(traced / len(rows))


def _reason_code_correctness(rows: list[dict[str, Any]]) -> float:
    denied_rows = [row for row in rows if str(row.get("decision", "")).strip() == "deny"]
    if not denied_rows:
        return 100.0
    with_reason = sum(
        1 for row in denied_rows if _reason_code(row).upper() not in {"", "UNKNOWN_REASON", "NONE"}
    )
    return _percent(with_reason / len(denied_rows))


def _stress_curve(policy_perf_payload: dict[str, Any]) -> str:
    points_raw = policy_perf_payload.get("scaling_curve")
    if not isinstance(points_raw, list):
        return "-"
    points = [point for point in points_raw if isinstance(point, dict)]
    if not points:
        return "-"
    parts: list[str] = []
    for point in sorted(points, key=lambda item: int(item.get("n_rules", 0))):
        n_rules = int(point.get("n_rules", 0))
        p95_ms = float(point.get("p95_ms", 0.0))
        parts.append(f"{n_rules}:{p95_ms:.4f}")
    return ", ".join(parts)


def _robustness_payload(
    rows: list[dict[str, Any]],
    *,
    matrix_path: Path,
) -> dict[str, Any]:
    grouped = _baseline_groups(rows)
    by_baseline: dict[str, dict[str, float | int]] = {}
    reason_counts: dict[str, int] = {}
    denied_but_executed_total = 0

    for baseline, baseline_rows in sorted(grouped.items()):
        attack_rows = [
            row
            for row in baseline_rows
            if str(row.get("category", "")).strip() in ATTACK_CATEGORIES
        ]
        attack_total = len(attack_rows)
        attack_blocked = sum(
            1 for row in attack_rows if str(row.get("decision", "")).strip() == "deny"
        )
        denied_but_executed = attack_total - attack_blocked
        denied_but_executed_total += denied_but_executed
        by_baseline[baseline] = {
            "attack_total": attack_total,
            "attack_blocked": attack_blocked,
            "attack_pass_rate": (attack_blocked / attack_total) if attack_total else 0.0,
            "denied_but_executed": denied_but_executed,
        }

    for row in rows:
        if str(row.get("decision", "")).strip() != "deny":
            continue
        reason = _reason_code(row)
        reason_counts[reason] = reason_counts.get(reason, 0) + 1

    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source_matrix": matrix_path.as_posix(),
        "attack_categories": sorted(ATTACK_CATEGORIES),
        "by_baseline": by_baseline,
        "denial_reason_counts": dict(
            sorted(reason_counts.items(), key=lambda item: (-item[1], item[0]))
        ),
        "denied_but_executed_total": denied_but_executed_total,
    }


def _results_markdown(
    *,
    matrix: dict[str, Any],
    matrix_path: Path,
    rows: list[dict[str, Any]],
    policy_perf_payload: dict[str, Any],
    robustness: dict[str, Any],
) -> str:
    grouped = _baseline_groups(rows)
    baselines = _ordered_baselines(rows)
    stress = _stress_curve(policy_perf_payload)
    by_baseline = robustness.get("by_baseline", {})
    if not isinstance(by_baseline, dict):
        by_baseline = {}

    policy_rows: list[str] = []
    trace_rows: list[str] = []
    reason_rows: list[str] = []
    stress_rows: list[str] = []
    robustness_rows: list[str] = []

    for baseline in baselines:
        baseline_rows = grouped.get(baseline, [])
        deny_allowed, allow_denied = _policy_decision_errors(baseline_rows)
        policy_rows.append(f"| {baseline} | {deny_allowed} | {allow_denied} |")
        trace_rows.append(f"| {baseline} | {_trace_completeness(baseline_rows):.2f} | |")
        reason_rows.append(f"| {baseline} | {_reason_code_correctness(baseline_rows):.2f} | |")
        stress_rows.append(f"| {baseline} | {stress} |")
        robust_data = by_baseline.get(baseline, {})
        pass_rate = (
            float(robust_data.get("attack_pass_rate", 0.0))
            if isinstance(robust_data, dict)
            else 0.0
        )
        robustness_rows.append(f"| {baseline} | {_percent(pass_rate):.2f} | |")

    return (
        "# Results Tables\n\n"
        "## Results Summary Table\n\n"
        "### Policy Decision Correctness\n\n"
        "| Baseline | Expected Deny → Allowed (should be 0) | Expected Allow → Denied (should be 0) |\n"
        "|---|---:|---:|\n"
        f"{chr(10).join(policy_rows)}\n\n"
        "### Trace Completeness\n\n"
        "| Baseline | TCR (%) | Notes |\n"
        "|---|---:|---|\n"
        f"{chr(10).join(trace_rows)}\n\n"
        "### Reason-Code Correctness\n\n"
        "| Baseline | Correct Reason-Code (%) | Notes |\n"
        "|---|---:|---|\n"
        f"{chr(10).join(reason_rows)}\n\n"
        "### Stress Scaling Curve (n rules p95_ms)\n\n"
        "| Baseline | Curve |\n"
        "|---|---|\n"
        f"{chr(10).join(stress_rows)}\n\n"
        "### Robustness Pass Rate (attack suite)\n\n"
        "| Baseline | Pass Rate (%) | Notes |\n"
        "|---|---:|---|\n"
        f"{chr(10).join(robustness_rows)}\n\n"
        "This file was generated by `scripts/generate_canonical_report.py`.\n\n"
        f"- Matrix input: `{matrix_path.as_posix()}`\n"
        f"- Keys: {sorted(list(matrix.keys()))}\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate canonical paper artifacts from benchmark matrix."
    )
    parser.add_argument("--matrix-input", required=True)
    parser.add_argument("--results-output", required=True)
    parser.add_argument("--policy-perf-json", required=True)
    parser.add_argument("--policy-perf-markdown", required=True)
    parser.add_argument("--robustness-output", required=True)
    parser.add_argument("--perf-iterations", type=int, default=5000)
    parser.add_argument("--perf-warmup", type=int, default=200)

    args = parser.parse_args(argv)

    matrix_path = Path(args.matrix_input)
    matrix = _load_matrix(matrix_path)
    rows = _matrix_rows(matrix)

    perf_payload = run_policy_engine_benchmark(
        iterations=args.perf_iterations,
        warmup=args.perf_warmup,
    )
    write_policy_engine_benchmark_outputs(
        perf_payload,
        json_path=Path(args.policy_perf_json),
        markdown_path=Path(args.policy_perf_markdown),
    )

    robustness = _robustness_payload(rows, matrix_path=matrix_path)
    _write_json(Path(args.robustness_output), robustness)

    markdown = _results_markdown(
        matrix=matrix,
        matrix_path=matrix_path,
        rows=rows,
        policy_perf_payload=perf_payload,
        robustness=robustness,
    )
    _write_text(Path(args.results_output), markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
