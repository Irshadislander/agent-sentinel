from __future__ import annotations

import json
import math
import random
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ATTACK_CATEGORIES = {
    "malicious",
    "policy_blocked",
    "malformed_payload",
    "plugin_failure",
    "trace_stress",
}
BASELINE_ORDER = [
    "default",
    "no_policy",
    "raw_errors",
    "no_trace",
    "allowlist_only",
    "no_gateway_enforcement",
]


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _matrix_rows(matrix_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows_payload = matrix_payload.get("rows")
    if isinstance(rows_payload, list):
        return [row for row in rows_payload if isinstance(row, dict)]

    grouped_payload = matrix_payload.get("grouped")
    if not isinstance(grouped_payload, dict):
        return []

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


def bootstrap_ci(
    values: list[float], iters: int = 2000, alpha: float = 0.05
) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    rng = random.Random(0)
    n = len(values)
    samples: list[float] = []
    for _ in range(iters):
        draw = [values[rng.randrange(n)] for _ in range(n)]
        samples.append(sum(draw) / n)
    samples.sort()
    lo = samples[int((alpha / 2) * iters)]
    hi = samples[int((1 - alpha / 2) * iters)]
    return lo, hi


def _bootstrap_percentile_ci(
    values: list[float], percentile: float, *, iters: int = 2000, alpha: float = 0.05
) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    rng = random.Random(0)
    n = len(values)
    samples: list[float] = []
    for _ in range(iters):
        draw = [values[rng.randrange(n)] for _ in range(n)]
        samples.append(_percentile(draw, percentile))
    samples.sort()
    lo = samples[int((alpha / 2) * iters)]
    hi = samples[int((1 - alpha / 2) * iters)]
    return lo, hi


def _bootstrap_delta_ci(
    lhs: list[float], rhs: list[float], *, iters: int = 2000, alpha: float = 0.05
) -> tuple[float, float]:
    if not lhs or not rhs:
        return (0.0, 0.0)
    rng = random.Random(0)
    n_lhs = len(lhs)
    n_rhs = len(rhs)
    samples: list[float] = []
    for _ in range(iters):
        lhs_draw = [lhs[rng.randrange(n_lhs)] for _ in range(n_lhs)]
        rhs_draw = [rhs[rng.randrange(n_rhs)] for _ in range(n_rhs)]
        samples.append((sum(lhs_draw) / n_lhs) - (sum(rhs_draw) / n_rhs))
    samples.sort()
    lo = samples[int((alpha / 2) * iters)]
    hi = samples[int((1 - alpha / 2) * iters)]
    return lo, hi


def _cohens_d(lhs: list[float], rhs: list[float]) -> float:
    if len(lhs) < 2 or len(rhs) < 2:
        return 0.0
    mean_lhs = sum(lhs) / len(lhs)
    mean_rhs = sum(rhs) / len(rhs)
    var_lhs = sum((v - mean_lhs) ** 2 for v in lhs) / (len(lhs) - 1)
    var_rhs = sum((v - mean_rhs) ** 2 for v in rhs) / (len(rhs) - 1)
    pooled_var = ((len(lhs) - 1) * var_lhs + (len(rhs) - 1) * var_rhs) / (len(lhs) + len(rhs) - 2)
    if pooled_var <= 0:
        return 0.0
    return (mean_lhs - mean_rhs) / math.sqrt(pooled_var)


def _row_reason_covered(row: dict[str, Any]) -> float:
    reason_code = str(row.get("reason_code", "")).strip()
    if reason_code and reason_code.upper() not in {"UNKNOWN_REASON", "NONE"}:
        return 1.0
    error_kind = str(row.get("error_kind", "")).strip().lower()
    return 1.0 if error_kind not in {"", "none", "unknown", "raw_error"} else 0.0


def _expected_decision(row: dict[str, Any]) -> str:
    return "allow" if str(row.get("category", "")).strip() == "benign" else "deny"


def _ordered_baselines(groups: dict[str, list[dict[str, Any]]]) -> list[str]:
    known = list(groups.keys())
    ordered = [b for b in BASELINE_ORDER if b in groups]
    ordered.extend(sorted(b for b in known if b not in ordered))
    return ordered


def _robust_attack_success(
    baseline: str,
    rows: list[dict[str, Any]],
    robustness_payload: dict[str, Any],
) -> float:
    by_baseline = robustness_payload.get("by_baseline")
    if isinstance(by_baseline, dict) and isinstance(by_baseline.get(baseline), dict):
        attack_pass_rate = float(by_baseline[baseline].get("attack_pass_rate", 0.0))
        return 1.0 - attack_pass_rate

    attack_rows = [row for row in rows if str(row.get("category", "")).strip() in ATTACK_CATEGORIES]
    if not attack_rows:
        return 0.0
    succeeded = sum(1 for row in attack_rows if str(row.get("decision", "")).strip() == "allow")
    return succeeded / len(attack_rows)


def _fmt_percent(v: float) -> str:
    return f"{(v * 100.0):.2f}"


def _fmt_ci(lo: float, hi: float, *, percent: bool) -> str:
    if percent:
        return f"[{lo * 100.0:.2f}, {hi * 100.0:.2f}]"
    return f"[{lo:.4f}, {hi:.4f}]"


def _ensure_artifacts_exist(bench_dir: Path) -> None:
    required = ["matrix.json", "robustness_report.json", "policy_engine_bench.json"]
    missing = [name for name in required if not (bench_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"missing required artifacts in {bench_dir}: {', '.join(missing)}")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    bench = root / "artifacts" / "bench"
    results_out = root / "paper" / "results_tables.md"
    stats_out = root / "paper" / "STATS_TABLES.md"

    _ensure_artifacts_exist(bench)
    matrix = _load_json(bench / "matrix.json")
    robustness = _load_json(bench / "robustness_report.json")
    perf = _load_json(bench / "policy_engine_bench.json")
    rows = _matrix_rows(matrix)
    if not rows:
        raise ValueError("matrix rows are empty")

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        baseline = str(row.get("baseline", "")).strip() or "unknown"
        groups[baseline].append(row)
    ordered_baselines = _ordered_baselines(groups)
    baseline_ref = "default" if "default" in groups else ordered_baselines[0]

    # Per-baseline vectors for CIs and effect-size deltas.
    vectors: dict[str, dict[str, list[float]]] = {}
    for baseline in ordered_baselines:
        baseline_rows = groups[baseline]
        correctness = [
            1.0 if str(row.get("decision", "")).strip() == _expected_decision(row) else 0.0
            for row in baseline_rows
        ]
        deny_expected = [row for row in baseline_rows if _expected_decision(row) == "deny"]
        unsafe = [
            1.0 if str(row.get("decision", "")).strip() == "allow" else 0.0 for row in deny_expected
        ] or [0.0]
        traces = [1.0 if bool(row.get("has_trace")) else 0.0 for row in baseline_rows]
        reason_coverage = [
            _row_reason_covered(row)
            for row in baseline_rows
            if str(row.get("decision", "")).strip() == "deny"
        ] or [1.0]
        rule_id_coverage = [1.0 if bool(row.get("rule_id")) else 0.0 for row in baseline_rows]
        latency = [float(row.get("duration_ms", 0.0)) for row in baseline_rows]
        attack_success = [_robust_attack_success(baseline, baseline_rows, robustness)]
        vectors[baseline] = {
            "correctness": correctness,
            "uer": unsafe,
            "tcr": traces,
            "reason_cov": reason_coverage,
            "rule_id_cov": rule_id_coverage,
            "latency": latency,
            "attack_success": attack_success,
        }

    ref = vectors[baseline_ref]
    summary_lines = [
        "# Results Tables",
        "",
        "## Results Summary (with 95% CI)",
        "",
        f"- Generated at (UTC): `{datetime.now(UTC).isoformat()}`",
        f"- Baseline reference for deltas/effect sizes: `{baseline_ref}`",
        "",
        "| Baseline | Decision Correctness % (95% CI) | UER % (95% CI) | TCR % (95% CI) | Reason-Code Coverage % (95% CI) | Explainability % with rule_id | Attack Success % | p50/p95/p99 ms |",
        "|---|---|---|---|---|---:|---:|---|",
    ]

    stats_lines = [
        "# Statistical Tables",
        "",
        "## Effect Sizes vs Baseline",
        "",
        f"Reference baseline: `{baseline_ref}`",
        "",
        "| Baseline | ΔUER | ΔTCR | ΔLatencyMean(ms) (95% CI) | Cohen's d (latency) |",
        "|---|---:|---:|---|---:|",
    ]

    for baseline in ordered_baselines:
        vec = vectors[baseline]
        correctness_mean = sum(vec["correctness"]) / len(vec["correctness"])
        correctness_ci = bootstrap_ci(vec["correctness"])
        uer_mean = sum(vec["uer"]) / len(vec["uer"])
        uer_ci = bootstrap_ci(vec["uer"])
        tcr_mean = sum(vec["tcr"]) / len(vec["tcr"])
        tcr_ci = bootstrap_ci(vec["tcr"])
        reason_mean = sum(vec["reason_cov"]) / len(vec["reason_cov"])
        reason_ci = bootstrap_ci(vec["reason_cov"])
        rule_id_mean = sum(vec["rule_id_cov"]) / len(vec["rule_id_cov"])
        attack_success_mean = vec["attack_success"][0]

        lat = vec["latency"]
        p50 = _percentile(lat, 0.50)
        p95 = _percentile(lat, 0.95)
        p99 = _percentile(lat, 0.99)
        summary_lines.append(
            f"| {baseline} | "
            f"{_fmt_percent(correctness_mean)} {_fmt_ci(*correctness_ci, percent=True)} | "
            f"{_fmt_percent(uer_mean)} {_fmt_ci(*uer_ci, percent=True)} | "
            f"{_fmt_percent(tcr_mean)} {_fmt_ci(*tcr_ci, percent=True)} | "
            f"{_fmt_percent(reason_mean)} {_fmt_ci(*reason_ci, percent=True)} | "
            f"{_fmt_percent(rule_id_mean)} | "
            f"{_fmt_percent(attack_success_mean)} | "
            f"{p50:.4f}/{p95:.4f}/{p99:.4f} |"
        )

        delta_uer = uer_mean - (sum(ref["uer"]) / len(ref["uer"]))
        delta_tcr = tcr_mean - (sum(ref["tcr"]) / len(ref["tcr"]))
        latency_mean = sum(lat) / len(lat)
        ref_latency_mean = sum(ref["latency"]) / len(ref["latency"])
        delta_latency = latency_mean - ref_latency_mean
        delta_latency_ci = _bootstrap_delta_ci(lat, ref["latency"])
        d_latency = _cohens_d(lat, ref["latency"])
        stats_lines.append(
            f"| {baseline} | {delta_uer:.4f} | {delta_tcr:.4f} | "
            f"{delta_latency:.4f} {_fmt_ci(*delta_latency_ci, percent=False)} | {d_latency:.4f} |"
        )

    stats_lines.extend(
        [
            "",
            "## Latency Percentile CIs (bootstrap 95%)",
            "",
            "| Baseline | p50_ms (95% CI) | p95_ms (95% CI) | p99_ms (95% CI) |",
            "|---|---|---|---|",
        ]
    )
    for baseline in ordered_baselines:
        lat = vectors[baseline]["latency"]
        p50 = _percentile(lat, 0.50)
        p95 = _percentile(lat, 0.95)
        p99 = _percentile(lat, 0.99)
        p50_ci = _bootstrap_percentile_ci(lat, 0.50)
        p95_ci = _bootstrap_percentile_ci(lat, 0.95)
        p99_ci = _bootstrap_percentile_ci(lat, 0.99)
        stats_lines.append(
            f"| {baseline} | {p50:.4f} {_fmt_ci(*p50_ci, percent=False)} | "
            f"{p95:.4f} {_fmt_ci(*p95_ci, percent=False)} | "
            f"{p99:.4f} {_fmt_ci(*p99_ci, percent=False)} |"
        )

    # Include stress/perf references from policy-engine bench payload.
    perf_cases = perf.get("cases", [])
    if isinstance(perf_cases, list) and perf_cases:
        stats_lines.extend(
            [
                "",
                "## Policy Engine Perf Cases",
                "",
                "| Case | mean_ms | p50_ms | p95_ms | p99_ms |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for case in perf_cases:
            if not isinstance(case, dict):
                continue
            stats_lines.append(
                f"| {case.get('case_id', '')} | "
                f"{float(case.get('mean_ms', 0.0)):.4f} | "
                f"{float(case.get('p50_ms', 0.0)):.4f} | "
                f"{float(case.get('p95_ms', 0.0)):.4f} | "
                f"{float(case.get('p99_ms', 0.0)):.4f} |"
            )

    results_out.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    stats_out.write_text("\n".join(stats_lines) + "\n", encoding="utf-8")
    print(f"Wrote: {results_out}")
    print(f"Wrote: {stats_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
