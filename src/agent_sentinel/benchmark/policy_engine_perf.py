from __future__ import annotations

import json
import statistics
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agent_sentinel.security.capabilities import FS_READ_PUBLIC, NET_HTTP_GET
from agent_sentinel.security.policy_engine import resolve_decision

DEFAULT_JSON_OUTPUT = Path("artifacts/bench/policy_engine_bench.json")
DEFAULT_MARKDOWN_OUTPUT = Path("paper/PERF_DAYXX.md")


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    index = (len(ordered) - 1) * percentile
    low = int(index)
    high = min(low + 1, len(ordered) - 1)
    weight = index - low
    return ordered[low] + (ordered[high] - ordered[low]) * weight


def _policy_cases() -> list[dict[str, Any]]:
    return [
        {
            "case_id": "allow_match_early",
            "capability": FS_READ_PUBLIC,
            "policy": {
                "rules": [
                    {
                        "rule_id": "allow_early",
                        "action": "allow",
                        "capabilities": [FS_READ_PUBLIC],
                    },
                    {"rule_id": "deny_late", "action": "deny", "capabilities": [FS_READ_PUBLIC]},
                ]
            },
        },
        {
            "case_id": "deny_match_early",
            "capability": FS_READ_PUBLIC,
            "policy": {
                "rules": [
                    {
                        "rule_id": "deny_early",
                        "action": "deny",
                        "capabilities": [FS_READ_PUBLIC],
                    },
                    {"rule_id": "allow_late", "action": "allow", "capabilities": [FS_READ_PUBLIC]},
                ]
            },
        },
        {
            "case_id": "no_match_default_deny",
            "capability": FS_READ_PUBLIC,
            "policy": {
                "rules": [
                    {
                        "rule_id": "allow_other",
                        "action": "allow",
                        "capabilities": [NET_HTTP_GET],
                    }
                ]
            },
        },
        {"case_id": "invalid_policy", "capability": FS_READ_PUBLIC, "policy": {}},
        {"case_id": "missing_policy", "capability": FS_READ_PUBLIC, "policy": None},
    ]


def run_policy_engine_benchmark(*, iterations: int = 5000, warmup: int = 200) -> dict[str, Any]:
    if iterations <= 0:
        raise ValueError("iterations must be > 0")
    if warmup < 0:
        raise ValueError("warmup must be >= 0")

    case_results: list[dict[str, Any]] = []
    for case in _policy_cases():
        case_id = str(case["case_id"])
        capability = str(case["capability"])
        policy = case["policy"]

        for _ in range(warmup):
            resolve_decision(capability, policy)

        durations_ms: list[float] = []
        trace_lengths: list[int] = []
        exemplar_decision = ""
        exemplar_reason_code = ""
        exemplar_rule_id: str | None = None
        for _ in range(iterations):
            result = resolve_decision(capability, policy)
            durations_ms.append(float(result.duration_ms))
            trace_lengths.append(len(result.evaluation_trace))
            exemplar_decision = result.decision
            exemplar_reason_code = result.reason_code
            exemplar_rule_id = result.rule_id

        case_results.append(
            {
                "case_id": case_id,
                "decision": exemplar_decision,
                "reason_code": exemplar_reason_code,
                "rule_id": exemplar_rule_id,
                "iterations": iterations,
                "warmup": warmup,
                "mean_ms": statistics.fmean(durations_ms),
                "p50_ms": _percentile(durations_ms, 0.50),
                "p95_ms": _percentile(durations_ms, 0.95),
                "p99_ms": _percentile(durations_ms, 0.99),
                "min_ms": min(durations_ms),
                "max_ms": max(durations_ms),
                "std_ms": statistics.pstdev(durations_ms) if len(durations_ms) > 1 else 0.0,
                "trace_len_mean": statistics.fmean(trace_lengths),
            }
        )

    case_results = sorted(case_results, key=lambda case: str(case["case_id"]))
    payload = {
        "benchmark": "policy_engine_perf",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "iterations": iterations,
        "warmup": warmup,
        "cases": case_results,
    }
    return payload


def render_policy_engine_markdown(payload: dict[str, Any], *, source_path: Path) -> str:
    cases_raw = payload.get("cases", [])
    cases = [case for case in cases_raw if isinstance(case, dict)]
    lines = [
        "# Policy Engine Performance",
        "",
        f"- Source JSON: `{source_path.as_posix()}`",
        f"- Generated at (UTC): `{payload.get('generated_at_utc', '')}`",
        f"- Iterations: `{payload.get('iterations', 0)}`",
        f"- Warmup: `{payload.get('warmup', 0)}`",
        "",
        (
            "| case | decision | reason_code | rule_id | mean_ms | "
            "p50_ms | p95_ms | p99_ms | trace_len_mean |"
        ),
        "|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for case in sorted(cases, key=lambda row: str(row.get("case_id", ""))):
        lines.append(
            f"| {case.get('case_id', '')} | {case.get('decision', '')} | "
            f"{case.get('reason_code', '')} | {case.get('rule_id', '') or '-'} | "
            f"{float(case.get('mean_ms', 0.0)):.6f} | "
            f"{float(case.get('p50_ms', 0.0)):.6f} | "
            f"{float(case.get('p95_ms', 0.0)):.6f} | "
            f"{float(case.get('p99_ms', 0.0)):.6f} | "
            f"{float(case.get('trace_len_mean', 0.0)):.2f} |"
        )
    lines.append("")
    return "\n".join(lines)


def write_policy_engine_benchmark_outputs(
    payload: dict[str, Any],
    *,
    json_path: Path = DEFAULT_JSON_OUTPUT,
    markdown_path: Path = DEFAULT_MARKDOWN_OUTPUT,
) -> tuple[Path, Path]:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    markdown = render_policy_engine_markdown(payload, source_path=json_path)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(markdown, encoding="utf-8")
    return json_path, markdown_path
