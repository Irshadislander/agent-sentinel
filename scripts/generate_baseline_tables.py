from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

DEFAULT_INPUT_PATH = Path("artifacts/baselines/baseline_suite.json")
DEFAULT_MARKDOWN_PATH = Path("paper/tables/table_baseline_comparison.md")
DEFAULT_CSV_PATH = Path("paper/tables/table_baseline_comparison.csv")
DEFAULT_LATEX_PATH = Path("paper/tables/evaluation_results.tex")
DISPLAY_ORDER = [
    "No Protection",
    "Static Allowlist",
    "Argument Allowlist",
    "Validator Only",
    "No Audit",
    "Progent-style",
    "Agent-Sentinel",
]


def _load_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("baseline suite payload must be a JSON object")
    return payload


def _ordered_systems(payload: dict[str, Any]) -> list[dict[str, Any]]:
    systems = payload.get("systems", [])
    if not isinstance(systems, list):
        raise ValueError("baseline suite payload missing systems list")
    by_label = {
        str(system.get("label", "")): system for system in systems if isinstance(system, dict)
    }
    return [by_label[label] for label in DISPLAY_ORDER if label in by_label]


def _format_number(value: Any) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "n/a"


def _render_markdown(payload: dict[str, Any], systems: list[dict[str, Any]]) -> str:
    lines = [
        "# Baseline Comparison",
        "",
        f"- Source: `{DEFAULT_INPUT_PATH.as_posix()}`",
        f"- Generated at (UTC): `{payload.get('generated_at_utc', 'unknown')}`",
        f"- Workload: `{payload.get('tasks_dir', 'unknown')}` ({payload.get('workload_scenario_count', 'unknown')} scenarios)",
        f"- Selection Note: {payload.get('workload_selection_reason', 'n/a')}",
        f"- Security deny categories: `{', '.join(payload.get('unsafe_categories', [])) or 'n/a'}`",
        f"- Robustness categories: `{', '.join(payload.get('robustness_categories', [])) or 'n/a'}`",
        "",
        "| System | Unsafe Actions Blocked (%) | Safe Actions Allowed (%) | Median Latency (ms) | p95 Latency (ms) | Notes |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for system in systems:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(system.get("label", "")),
                    _format_number(system.get("unsafe_actions_blocked_pct")),
                    _format_number(system.get("safe_actions_allowed_pct")),
                    _format_number(system.get("median_latency_ms")),
                    _format_number(system.get("p95_latency_ms")),
                    str(system.get("notes", "")).replace("|", "\\|"),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def _render_latex(systems: list[dict[str, Any]]) -> str:
    lines = [
        "\\begin{table*}[t]",
        "\\centering",
        "\\small",
        "\\setlength{\\tabcolsep}{7pt}",
        "\\caption{Baseline comparison across the Agent-Sentinel evaluation suite. The table reports attack blocking effectiveness, safe-action allowance, and runtime latency across different defense configurations.}",
        "\\label{tab:evaluation_results}",
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        "System & Unsafe Actions Blocked (\\%) & Safe Actions Allowed (\\%) & Median Latency (ms) & p95 Latency (ms) \\\\",
        "\\midrule",
    ]
    for system in systems:
        label = str(system.get("label", ""))
        blocked = _format_number(system.get("unsafe_actions_blocked_pct"))
        safe = _format_number(system.get("safe_actions_allowed_pct"))
        median = _format_number(system.get("median_latency_ms"))
        p95 = _format_number(system.get("p95_latency_ms"))
        if label == "Agent-Sentinel":
            lines.append(
                f"\\textbf{{{label}}} & \\textbf{{{blocked}}} & \\textbf{{{safe}}} & {median} & {p95} \\\\"
            )
        else:
            lines.append(f"{label} & {blocked} & {safe} & {median} & {p95} \\\\")
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\end{table*}",
            "",
        ]
    )
    return "\n".join(lines)


def generate_tables(
    *,
    input_path: Path = DEFAULT_INPUT_PATH,
    markdown_path: Path = DEFAULT_MARKDOWN_PATH,
    csv_path: Path = DEFAULT_CSV_PATH,
    latex_path: Path = DEFAULT_LATEX_PATH,
) -> tuple[Path, Path, Path]:
    payload = _load_payload(input_path)
    systems = _ordered_systems(payload)

    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(_render_markdown(payload, systems), encoding="utf-8")

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "System",
                "Unsafe Actions Blocked (%)",
                "Safe Actions Allowed (%)",
                "Median Latency (ms)",
                "p95 Latency (ms)",
                "unsafe_total",
                "unsafe_blocked_count",
                "safe_total",
                "safe_allowed_count",
                "robustness_total",
                "robustness_blocked_count",
                "robustness_error_count",
                "robustness_success_count",
                "execution_error_count",
                "scenario_count",
                "Notes",
            ],
        )
        writer.writeheader()
        for system in systems:
            writer.writerow(
                {
                    "System": system.get("label", ""),
                    "Unsafe Actions Blocked (%)": _format_number(
                        system.get("unsafe_actions_blocked_pct")
                    ),
                    "Safe Actions Allowed (%)": _format_number(
                        system.get("safe_actions_allowed_pct")
                    ),
                    "Median Latency (ms)": _format_number(system.get("median_latency_ms")),
                    "p95 Latency (ms)": _format_number(system.get("p95_latency_ms")),
                    "unsafe_total": system.get("unsafe_total", 0),
                    "unsafe_blocked_count": system.get("unsafe_blocked_count", 0),
                    "safe_total": system.get("safe_total", 0),
                    "safe_allowed_count": system.get("safe_allowed_count", 0),
                    "robustness_total": system.get("robustness_total", 0),
                    "robustness_blocked_count": system.get("robustness_blocked_count", 0),
                    "robustness_error_count": system.get("robustness_error_count", 0),
                    "robustness_success_count": system.get("robustness_success_count", 0),
                    "execution_error_count": system.get("execution_error_count", 0),
                    "scenario_count": system.get("scenario_count", 0),
                    "Notes": system.get("notes", ""),
                }
            )

    latex_path.parent.mkdir(parents=True, exist_ok=True)
    latex_path.write_text(_render_latex(systems), encoding="utf-8")

    return markdown_path, csv_path, latex_path


def main() -> int:
    markdown_path, csv_path, latex_path = generate_tables()
    print(f"Baseline markdown table: {markdown_path}")
    print(f"Baseline CSV table: {csv_path}")
    print(f"Baseline LaTeX table: {latex_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
