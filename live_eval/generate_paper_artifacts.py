from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LIVE_RESULTS_CSV = ROOT / "live_eval" / "results" / "live_results_80x5.csv"
DEFAULT_LIVE_SUMMARY_JSON = ROOT / "live_eval" / "results" / "live_summary_80x5.json"
DEFAULT_STRESS_RESULTS_CSV = ROOT / "live_eval" / "results" / "live_results_5k.csv"
DEFAULT_STRESS_SUMMARY_JSON = ROOT / "live_eval" / "results" / "live_summary_5k.json"
DEFAULT_TABLES_DIR = ROOT / "paper" / "tables"
DEFAULT_FIGURES_DIR = ROOT / "paper" / "figures"


def _load_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"results CSV not found: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [row for row in reader if row]
    if not rows:
        raise SystemExit(f"results CSV is empty: {path}")
    return rows


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"summary JSON not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"summary JSON must contain an object: {path}")
    return payload


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"cannot parse float from {value!r}") from exc


def _mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def _stdev(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) > 1 else 0.0


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    index = (len(ordered) - 1) * p
    low = math.floor(index)
    high = math.ceil(index)
    if low == high:
        return ordered[low]
    weight = index - low
    return ordered[low] + (ordered[high] - ordered[low]) * weight


def _percentile_nearest_rank(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(1, math.ceil(p * len(ordered)))
    return ordered[rank - 1]


def _latex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    escaped = text
    for src, dst in replacements.items():
        escaped = escaped.replace(src, dst)
    return escaped


def _task_rows(rows: list[dict[str, str]], task_type: str) -> list[dict[str, str]]:
    return [row for row in rows if row.get("type", "").strip() == task_type]


def _compute_overall_metrics(rows: list[dict[str, str]]) -> dict[str, Any]:
    benign_rows = _task_rows(rows, "benign")
    attack_rows = _task_rows(rows, "attack")
    robustness_rows = _task_rows(rows, "robustness")

    benign_allowed = sum(row.get("actual_outcome") == "ALLOW" for row in benign_rows)
    attack_denied = sum(row.get("actual_outcome") == "DENY" for row in attack_rows)
    attack_blocked = sum(_bool(row.get("blocked")) for row in attack_rows)
    attack_model_denied = sum(
        row.get("actual_outcome") == "DENY" and not _bool(row.get("blocked")) for row in attack_rows
    )
    robustness_success = sum(_bool(row.get("success")) for row in robustness_rows)

    latencies = [_float(row.get("latency_ms")) for row in rows]

    return {
        "total_tasks": len(rows),
        "total_benign_tasks": len(benign_rows),
        "total_attack_tasks": len(attack_rows),
        "total_robustness_tasks": len(robustness_rows),
        "benign_preservation_rate": benign_allowed / len(benign_rows) if benign_rows else 0.0,
        "attack_prevention_rate": attack_denied / len(attack_rows) if attack_rows else 0.0,
        "explicit_sentinel_block_rate_on_attacks": attack_blocked / len(attack_rows)
        if attack_rows
        else 0.0,
        "model_self_denial_rate_on_attacks": attack_model_denied / len(attack_rows)
        if attack_rows
        else 0.0,
        "robustness_handled_rate": robustness_success / len(robustness_rows)
        if robustness_rows
        else 0.0,
        "model_no_tool_denials_on_attacks": attack_model_denied,
        "median_latency_ms": _percentile(latencies, 0.50),
        "p95_latency_ms": _percentile(latencies, 0.95),
        "max_latency_ms": max(latencies) if latencies else 0.0,
    }


def _compute_run_metrics(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    run_ids = sorted({int(row.get("run_id", "0")) for row in rows})
    metrics: list[dict[str, Any]] = []
    for run_id in run_ids:
        subset = [row for row in rows if int(row.get("run_id", "0")) == run_id]
        benign_rows = _task_rows(subset, "benign")
        attack_rows = _task_rows(subset, "attack")
        robustness_rows = _task_rows(subset, "robustness")

        benign_allowed = sum(row.get("actual_outcome") == "ALLOW" for row in benign_rows)
        attack_denied = sum(row.get("actual_outcome") == "DENY" for row in attack_rows)
        attack_blocked = sum(_bool(row.get("blocked")) for row in attack_rows)
        attack_model_denied = sum(
            row.get("actual_outcome") == "DENY" and not _bool(row.get("blocked"))
            for row in attack_rows
        )
        robustness_success = sum(_bool(row.get("success")) for row in robustness_rows)
        latencies = [_float(row.get("latency_ms")) for row in subset]

        metrics.append(
            {
                "run_id": run_id,
                "benign_preservation_rate": benign_allowed / len(benign_rows)
                if benign_rows
                else 0.0,
                "attack_prevention_rate": attack_denied / len(attack_rows) if attack_rows else 0.0,
                "explicit_sentinel_block_rate_on_attacks": attack_blocked / len(attack_rows)
                if attack_rows
                else 0.0,
                "model_self_denial_rate_on_attacks": attack_model_denied / len(attack_rows)
                if attack_rows
                else 0.0,
                "robustness_handled_rate": robustness_success / len(robustness_rows)
                if robustness_rows
                else 0.0,
                "median_latency_ms": _percentile(latencies, 0.50),
                "p95_latency_ms": _percentile_nearest_rank(latencies, 0.95),
            }
        )
    return metrics


def _summarize_run_metrics(run_metrics: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    keys = [
        "benign_preservation_rate",
        "attack_prevention_rate",
        "explicit_sentinel_block_rate_on_attacks",
        "model_self_denial_rate_on_attacks",
        "robustness_handled_rate",
        "median_latency_ms",
        "p95_latency_ms",
    ]
    summary: dict[str, dict[str, float]] = {}
    for key in keys:
        values = [float(item[key]) for item in run_metrics]
        summary[key] = {"mean": _mean(values), "std": _stdev(values)}
    return summary


def _attack_breakdown(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    attack_rows = _task_rows(rows, "attack")
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in attack_rows:
        grouped[row.get("category", "unknown").strip() or "unknown"].append(row)

    breakdown: list[dict[str, Any]] = []
    for category in sorted(grouped, key=lambda name: (-len(grouped[name]), name)):
        category_rows = grouped[category]
        total = len(category_rows)
        denied = sum(row.get("actual_outcome") == "DENY" for row in category_rows)
        blocked = sum(_bool(row.get("blocked")) for row in category_rows)
        breakdown.append(
            {
                "category": category,
                "total": total,
                "deny": denied,
                "blocked": blocked,
                "blocked_rate": (blocked / total * 100.0) if total else 0.0,
            }
        )
    return breakdown


def _validate_summary_against_csv(
    summary: dict[str, Any],
    computed: dict[str, Any],
    *,
    label: str,
) -> None:
    mismatches: list[str] = []
    for key, actual in summary.items():
        if key not in computed:
            mismatches.append(f"{key}: missing")
            continue
        expected = computed[key]
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            if abs(float(actual) - float(expected)) > 1e-6:
                mismatches.append(f"{key}: expected {expected}, got {actual}")
        elif actual != expected:
            mismatches.append(f"{key}: expected {expected}, got {actual}")
    if mismatches:
        joined = "; ".join(mismatches)
        raise SystemExit(f"{label} does not match computed values: {joined}")


def _format_percent(value: float, digits: int = 1) -> str:
    return f"{value * 100.0:.{digits}f}\\%"


def _format_float(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}"


ROW_BREAK = r"\\"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def _render_summary_table(
    summary: dict[str, Any],
    *,
    caption: str = "Live OpenAI-backed evaluation summary for the 80x5 benchmark.",
    label: str = "tab:live_eval_summary",
    explicit_block_digits: int = 1,
) -> str:
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\small",
        r"\renewcommand{\arraystretch}{1.12}",
        r"\setlength{\tabcolsep}{6pt}",
        rf"\caption{{{caption}}}",
        rf"\label{{{label}}}",
        r"\begin{tabular}{@{}p{0.74\linewidth}r@{}}",
        r"\toprule",
        r"Metric & Value \\",
        r"\midrule",
        f"Total live executions & {int(summary['total_tasks'])} {ROW_BREAK}",
        f"Benign tasks & {int(summary['total_benign_tasks'])} {ROW_BREAK}",
        f"Attack tasks & {int(summary['total_attack_tasks'])} {ROW_BREAK}",
        f"Robustness tasks & {int(summary['total_robustness_tasks'])} {ROW_BREAK}",
        r"\addlinespace",
        f"Benign preservation rate & {_format_percent(float(summary['benign_preservation_rate']))} {ROW_BREAK}",
        f"Attack prevention rate & {_format_percent(float(summary['attack_prevention_rate']))} {ROW_BREAK}",
        f"Explicit Sentinel block rate on attacks & {_format_percent(float(summary['explicit_sentinel_block_rate_on_attacks']), digits=explicit_block_digits)} {ROW_BREAK}",
        f"Model no-tool denials on attacks & {int(summary['model_no_tool_denials_on_attacks'])} {ROW_BREAK}",
        r"\addlinespace",
        f"Median latency & {_format_float(float(summary['median_latency_ms']), digits=1)} ms {ROW_BREAK}",
        f"P95 latency & {_format_float(float(summary['p95_latency_ms']), digits=1)} ms {ROW_BREAK}",
        f"Max latency & {_format_float(float(summary['max_latency_ms']), digits=1)} ms {ROW_BREAK}",
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
        "",
    ]
    return "\n".join(lines)


def _render_main_results_table(summary: dict[str, Any]) -> str:
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\small",
        r"\renewcommand{\arraystretch}{1.12}",
        r"\setlength{\tabcolsep}{6pt}",
        r"\caption{Main results for the 80x5 live evaluation.}",
        r"\label{tab:live_eval_main_results}",
        r"\begin{tabular}{@{}p{0.71\linewidth}r@{}}",
        r"\toprule",
        r"Metric & Result \\",
        r"\midrule",
        f"Total live executions & {int(summary['total_tasks'])} {ROW_BREAK}",
        f"Benign tasks & {int(summary['total_benign_tasks'])} {ROW_BREAK}",
        f"Attack tasks & {int(summary['total_attack_tasks'])} {ROW_BREAK}",
        f"Robustness tasks & {int(summary['total_robustness_tasks'])} {ROW_BREAK}",
        r"\addlinespace",
        f"Benign preservation rate & {_format_percent(float(summary['benign_preservation_rate']))} {ROW_BREAK}",
        f"Attack prevention rate & {_format_percent(float(summary['attack_prevention_rate']))} {ROW_BREAK}",
        f"Explicit Sentinel block rate on attacks & {_format_percent(float(summary['explicit_sentinel_block_rate_on_attacks']))} {ROW_BREAK}",
        f"Model-only denials & {int(summary['model_no_tool_denials_on_attacks'])} {ROW_BREAK}",
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
        "",
    ]
    return "\n".join(lines)


def _render_stability_table(run_summary: dict[str, dict[str, float]]) -> str:
    rows = [
        ("Benign preservation rate", run_summary["benign_preservation_rate"]),
        ("Attack prevention rate", run_summary["attack_prevention_rate"]),
        (
            "Explicit Sentinel block rate on attacks",
            run_summary["explicit_sentinel_block_rate_on_attacks"],
        ),
        ("Median latency", run_summary["median_latency_ms"]),
        ("P95 latency", run_summary["p95_latency_ms"]),
    ]
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\small",
        r"\renewcommand{\arraystretch}{1.12}",
        r"\setlength{\tabcolsep}{6pt}",
        r"\caption{Run-to-run stability of the 80x5 live evaluation.}",
        r"\label{tab:live_eval_stability}",
        r"\begin{tabular}{@{}p{0.67\linewidth}r@{}}",
        r"\toprule",
        r"Metric & Mean $\pm$ Std \\",
        r"\midrule",
    ]
    for label, stats in rows:
        mean_value = stats["mean"]
        std_value = stats["std"]
        if "latency" in label.lower():
            cell = f"{_format_float(mean_value)} $\\pm$ {_format_float(std_value)} ms"
        else:
            cell = f"{_format_percent(mean_value)} $\\pm$ {_format_percent(std_value)}"
        lines.append(f"{label} & {cell} {ROW_BREAK}")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}", ""])
    return "\n".join(lines)


def _render_attack_breakdown_table(breakdown: list[dict[str, Any]]) -> str:
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\small",
        r"\renewcommand{\arraystretch}{1.1}",
        r"\setlength{\tabcolsep}{6pt}",
        r"\caption{Attack-category breakdown of the 80x5 live evaluation.}",
        r"\label{tab:live_attack_breakdown}",
        r"\begin{tabular}{@{}lrrrr@{}}",
        r"\toprule",
        r"Category & Total & Deny & Blocked & Blocked Rate (\%) \\",
        r"\midrule",
    ]
    for row in breakdown:
        category = f"\\texttt{{{_latex_escape(str(row['category']))}}}"
        lines.append(
            f"{category} & {int(row['total'])} & {int(row['deny'])} & {int(row['blocked'])} & {row['blocked_rate']:.1f} {ROW_BREAK}"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}", ""])
    return "\n".join(lines)


def _render_stress_table(summary: dict[str, Any]) -> str:
    return _render_summary_table(
        summary,
        caption="Live OpenAI-backed stress evaluation over 5,000 executions.",
        label="tab:live_eval_stress_5k",
        explicit_block_digits=2,
    )


def _render_notes() -> str:
    return "\n".join(
        [
            "# Live Evaluation Notes",
            "",
            "- `tab_live_eval_summary.tex` is the aggregate count-and-rate summary for the 80x5 OpenAI-backed live evaluation. It reports the total number of executions, task counts by class, attack blocking, model-side denials, and latency statistics.",
            "- `tab_live_eval_main_results.tex` is the paper-facing results table. It highlights the primary safety claims and keeps the presentation compact for the Evaluation section.",
            "- `tab_live_eval_stability.tex` reports mean $\\pm$ std across the five runs so the manuscript can discuss run-to-run stability instead of a single point estimate.",
            "- `tab_live_attack_breakdown.tex` summarizes the attack-only slice by category, showing total cases, total denials, explicit Sentinel blocks, and the resulting blocked rate.",
            "- `tab_live_eval_stress_5k.tex` summarizes the 5,000-execution stress evaluation used to report large-scale live performance.",
            "- `fig_live_eval_outcomes.png` visualizes the aggregate outcome composition by task type.",
            "- `fig_live_eval_latency_boxplot.png` shows the latency distribution by task type.",
            "",
        ]
    )


def _render_figure_tex(
    *,
    label: str,
    caption: str,
    graphic_path: str,
) -> str:
    return "\n".join(
        [
            r"\begin{figure}[t]",
            r"\centering",
            rf"\includegraphics[width=\linewidth]{{{graphic_path}}}",
            rf"\caption{{{caption}}}",
            rf"\label{{{label}}}",
            r"\end{figure}",
            "",
        ]
    )


def _load_font(size: int, *, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    candidates: list[str]
    if mono:
        candidates = [
            "/System/Library/Fonts/Supplemental/Andale Mono.ttf",
            "/System/Library/Fonts/Supplemental/Courier.ttc",
            "/System/Library/Fonts/Supplemental/Courier New.ttf",
        ]
    elif bold:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Supplemental/Arial Black.ttf",
            "/System/Library/Fonts/Supplemental/Helvetica.ttc",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Helvetica.ttc",
            "/System/Library/Fonts/Supplemental/Avenir.ttc",
        ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _text_box(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _draw_centered_text(
    draw: ImageDraw.ImageDraw,
    center_x: float,
    top_y: float,
    text: str,
    font: ImageFont.ImageFont,
    fill: str = "#111827",
) -> None:
    width, height = _text_box(draw, text, font)
    draw.text((center_x - width / 2.0, top_y), text, font=font, fill=fill)


def _value_to_y(value: float, *, top: int, height: int, y_max: float) -> float:
    if y_max <= 0:
        return top + height
    return top + height - (value / y_max) * height


def _draw_legend(
    draw: ImageDraw.ImageDraw,
    *,
    x: int,
    y: int,
    items: list[tuple[str, str]],
    font: ImageFont.ImageFont,
    item_gap: int = 24,
    box_size: int = 18,
) -> None:
    cursor_x = x
    for label, color in items:
        draw.rectangle(
            [cursor_x, y + 2, cursor_x + box_size, y + 2 + box_size], fill=color, outline="#1f2933"
        )
        draw.text((cursor_x + box_size + 8, y), label, font=font, fill="#111827")
        label_width, _ = _text_box(draw, label, font)
        cursor_x += box_size + 8 + label_width + item_gap


def _generate_outcomes_figure(rows: list[dict[str, str]], out_path: Path) -> None:
    task_types = ["benign", "attack", "robustness"]
    labels = ["Benign Tasks", "Attack Tasks", "Robustness Tasks"]
    colors = {"allowed": "#7B9BBE", "blocked": "#A4AFBC", "denied": "#D3D3D3"}

    allowed_counts: list[int] = []
    blocked_counts: list[int] = []
    denied_counts: list[int] = []
    for task_type in task_types:
        subset = _task_rows(rows, task_type)
        allowed_counts.append(sum(row.get("actual_outcome") == "ALLOW" for row in subset))
        blocked_counts.append(sum(_bool(row.get("blocked")) for row in subset))
        denied_counts.append(
            sum(
                row.get("actual_outcome") == "DENY" and not _bool(row.get("blocked"))
                for row in subset
            )
        )
    total_counts = [
        allowed_counts[idx] + blocked_counts[idx] + denied_counts[idx]
        for idx in range(len(task_types))
    ]

    width, height = 1600, 900
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    axis_font = _load_font(19)
    tick_font = _load_font(16)
    legend_font = _load_font(17)

    plot_left, plot_top, plot_right, plot_bottom = 160, 140, 1510, 720
    plot_height = plot_bottom - plot_top

    max_total = max(total_counts) if total_counts else 0.0
    y_max = max(20.0, math.ceil(max_total * 1.1 / 10.0) * 10.0)
    tick_step = 50 if y_max <= 250 else 100
    tick_values = list(range(0, int(y_max) + 1, tick_step))
    for tick in tick_values:
        y = _value_to_y(tick, top=plot_top, height=plot_height, y_max=y_max)
        draw.line([(plot_left, y), (plot_right, y)], fill="#E5E7EB", width=2)
        label = f"{tick}"
        text_width, text_height = _text_box(draw, label, tick_font)
        draw.text(
            (plot_left - 16 - text_width, y - text_height / 2.0),
            label,
            font=tick_font,
            fill="#374151",
        )

    draw.line([(plot_left, plot_top), (plot_left, plot_bottom)], fill="#111827", width=2)
    draw.line([(plot_left, plot_bottom), (plot_right, plot_bottom)], fill="#111827", width=2)

    bar_width = 240
    centers = [460, 840, 1220]
    segment_names = ["Allowed", "Sentinel blocked", "Model no-tool denial"]
    segment_colors = [colors["allowed"], colors["blocked"], colors["denied"]]

    for idx, center_x in enumerate(centers):
        bar_left = center_x - bar_width / 2.0
        current_value = 0.0
        segments = [allowed_counts[idx], blocked_counts[idx], denied_counts[idx]]
        for seg_value, color in zip(segments, segment_colors, strict=False):
            if seg_value <= 0:
                continue
            seg_top = _value_to_y(
                current_value + seg_value, top=plot_top, height=plot_height, y_max=y_max
            )
            seg_bottom = _value_to_y(current_value, top=plot_top, height=plot_height, y_max=y_max)
            draw.rectangle(
                [bar_left, seg_top, bar_left + bar_width, seg_bottom],
                fill=color,
                outline="#1F2937",
                width=2,
            )
            current_value += seg_value

        label_text = labels[idx]
        label_width, _ = _text_box(draw, label_text, axis_font)
        draw.text(
            (center_x - label_width / 2.0, plot_bottom + 14),
            label_text,
            font=axis_font,
            fill="#111827",
        )

    _draw_legend(
        draw,
        x=plot_left + 45,
        y=92,
        items=list(zip(segment_names, segment_colors, strict=False)),
        font=legend_font,
        item_gap=22,
        box_size=16,
    )

    ylabel_font = _load_font(19)
    draw.text(
        (40, plot_top + plot_height / 2.0 - 10), "Executions", font=ylabel_font, fill="#111827"
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path, format="PNG")


def _generate_latency_figure(rows: list[dict[str, str]], out_path: Path) -> None:
    task_types = ["benign", "attack", "robustness"]
    labels = ["Benign Tasks", "Attack Tasks", "Robustness Tasks"]
    data = [
        [_float(row.get("latency_ms")) for row in _task_rows(rows, task_type)]
        for task_type in task_types
    ]

    width, height = 1600, 900
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    axis_font = _load_font(19)
    tick_font = _load_font(16)

    plot_left, plot_top, plot_right, plot_bottom = 160, 140, 1510, 720
    plot_height = plot_bottom - plot_top

    y_values = [value for group in data for value in group]
    y_max = math.ceil(max(y_values) / 1000.0) * 1000.0
    if y_max <= 0:
        y_max = 1000.0
    tick_step = 2000.0 if y_max > 5000 else 1000.0
    ticks = [tick for tick in range(0, int(y_max) + 1, int(tick_step))]
    if ticks[-1] != y_max:
        ticks.append(int(y_max))

    for tick in ticks:
        y = _value_to_y(float(tick), top=plot_top, height=plot_height, y_max=y_max)
        draw.line([(plot_left, y), (plot_right, y)], fill="#E5E7EB", width=2)
        label = f"{tick}"
        text_width, text_height = _text_box(draw, label, tick_font)
        draw.text(
            (plot_left - 18 - text_width, y - text_height / 2.0),
            label,
            font=tick_font,
            fill="#374151",
        )

    draw.line([(plot_left, plot_top), (plot_left, plot_bottom)], fill="#111827", width=2)
    draw.line([(plot_left, plot_bottom), (plot_right, plot_bottom)], fill="#111827", width=2)

    box_width = 210
    centers = [460, 840, 1220]
    box_colors = ["#8FA7C2", "#C3CBD4", "#D5DEC9"]
    for idx, values in enumerate(data):
        if not values:
            continue
        ordered = sorted(values)
        q1 = _percentile(ordered, 0.25)
        med = _percentile(ordered, 0.50)
        q3 = _percentile(ordered, 0.75)
        vmin = ordered[0]
        vmax = ordered[-1]
        center_x = centers[idx]
        left = center_x - box_width / 2.0
        right = center_x + box_width / 2.0
        q1_y = _value_to_y(q1, top=plot_top, height=plot_height, y_max=y_max)
        q3_y = _value_to_y(q3, top=plot_top, height=plot_height, y_max=y_max)
        med_y = _value_to_y(med, top=plot_top, height=plot_height, y_max=y_max)
        min_y = _value_to_y(vmin, top=plot_top, height=plot_height, y_max=y_max)
        max_y = _value_to_y(vmax, top=plot_top, height=plot_height, y_max=y_max)

        draw.rectangle([left, q3_y, right, q1_y], fill=box_colors[idx], outline="#1f2933", width=2)
        draw.line([(left, med_y), (right, med_y)], fill="#111827", width=3)
        draw.line([(center_x, max_y), (center_x, q3_y)], fill="#374151", width=2)
        draw.line([(center_x, q1_y), (center_x, min_y)], fill="#374151", width=2)
        cap_half = 36
        draw.line(
            [(center_x - cap_half, max_y), (center_x + cap_half, max_y)], fill="#374151", width=2
        )
        draw.line(
            [(center_x - cap_half, min_y), (center_x + cap_half, min_y)], fill="#374151", width=2
        )

        label_text = labels[idx]
        label_width, _ = _text_box(draw, label_text, axis_font)
        draw.text(
            (center_x - label_width / 2.0, plot_bottom + 14),
            label_text,
            font=axis_font,
            fill="#111827",
        )

    draw.text(
        (40, plot_top + plot_height / 2.0 - 10), "Latency (ms)", font=axis_font, fill="#111827"
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path, format="PNG")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate paper-ready live evaluation artifacts.")
    parser.add_argument(
        "--results-csv",
        default=str(DEFAULT_LIVE_RESULTS_CSV),
        help=f"Path to the 80x5 results CSV (default: {DEFAULT_LIVE_RESULTS_CSV})",
    )
    parser.add_argument(
        "--summary-json",
        default=str(DEFAULT_LIVE_SUMMARY_JSON),
        help=f"Path to the 80x5 summary JSON (default: {DEFAULT_LIVE_SUMMARY_JSON})",
    )
    parser.add_argument(
        "--stress-results-csv",
        default=str(DEFAULT_STRESS_RESULTS_CSV),
        help=f"Path to the 5k stress results CSV (default: {DEFAULT_STRESS_RESULTS_CSV})",
    )
    parser.add_argument(
        "--stress-summary-json",
        default=str(DEFAULT_STRESS_SUMMARY_JSON),
        help=f"Path to the 5k stress summary JSON (default: {DEFAULT_STRESS_SUMMARY_JSON})",
    )
    parser.add_argument(
        "--tables-dir",
        default=str(DEFAULT_TABLES_DIR),
        help=f"Output directory for paper tables (default: {DEFAULT_TABLES_DIR})",
    )
    parser.add_argument(
        "--figures-dir",
        default=str(DEFAULT_FIGURES_DIR),
        help=f"Output directory for paper figures (default: {DEFAULT_FIGURES_DIR})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    results_csv = Path(args.results_csv)
    summary_json = Path(args.summary_json)
    stress_results_csv = Path(args.stress_results_csv)
    stress_summary_json = Path(args.stress_summary_json)
    tables_dir = Path(args.tables_dir)
    figures_dir = Path(args.figures_dir)

    rows = _load_csv_rows(results_csv)
    summary_payload = _load_json(summary_json)
    computed_summary = _compute_overall_metrics(rows)
    _validate_summary_against_csv(summary_payload, computed_summary, label=str(summary_json))

    stress_rows = _load_csv_rows(stress_results_csv)
    stress_summary_payload = _load_json(stress_summary_json)
    stress_computed_summary = _compute_overall_metrics(stress_rows)
    _validate_summary_against_csv(
        stress_summary_payload,
        stress_computed_summary,
        label=str(stress_summary_json),
    )

    run_metrics = _compute_run_metrics(rows)
    run_summary = _summarize_run_metrics(run_metrics)
    attack_breakdown = _attack_breakdown(rows)

    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    summary_tex = _render_summary_table(summary_payload)
    main_results_tex = _render_main_results_table(computed_summary)
    stability_tex = _render_stability_table(run_summary)
    attack_breakdown_tex = _render_attack_breakdown_table(attack_breakdown)
    stress_tex = _render_stress_table(stress_summary_payload)
    notes_md = _render_notes()

    outcomes_png = figures_dir / "fig_live_eval_outcomes.png"
    latency_png = figures_dir / "fig_live_eval_latency_boxplot.png"
    _generate_outcomes_figure(rows, outcomes_png)
    _generate_latency_figure(rows, latency_png)

    outcomes_tex = _render_figure_tex(
        label="fig:live_eval_outcomes",
        caption="Outcome composition in the 80x5 live evaluation.",
        graphic_path="figures/fig_live_eval_outcomes.png",
    )
    latency_tex = _render_figure_tex(
        label="fig:live_eval_latency_boxplot",
        caption="Latency distribution across the 80x5 live evaluation.",
        graphic_path="figures/fig_live_eval_latency_boxplot.png",
    )

    _write(tables_dir / "tab_live_eval_summary.tex", summary_tex)
    _write(tables_dir / "tab_live_eval_main_results.tex", main_results_tex)
    _write(tables_dir / "tab_live_eval_stability.tex", stability_tex)
    _write(tables_dir / "tab_live_attack_breakdown.tex", attack_breakdown_tex)
    _write(tables_dir / "tab_live_eval_stress_5k.tex", stress_tex)
    _write(tables_dir / "live_eval_notes.md", notes_md)
    _write(figures_dir / "fig_live_eval_outcomes.tex", outcomes_tex)
    _write(figures_dir / "fig_live_eval_latency_boxplot.tex", latency_tex)

    print(f"Wrote {tables_dir / 'tab_live_eval_summary.tex'}")
    print(f"Wrote {tables_dir / 'tab_live_eval_main_results.tex'}")
    print(f"Wrote {tables_dir / 'tab_live_eval_stability.tex'}")
    print(f"Wrote {tables_dir / 'tab_live_attack_breakdown.tex'}")
    print(f"Wrote {tables_dir / 'tab_live_eval_stress_5k.tex'}")
    print(f"Wrote {tables_dir / 'live_eval_notes.md'}")
    print(f"Wrote {outcomes_png}")
    print(f"Wrote {latency_png}")
    print(f"Wrote {figures_dir / 'fig_live_eval_outcomes.tex'}")
    print(f"Wrote {figures_dir / 'fig_live_eval_latency_boxplot.tex'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
