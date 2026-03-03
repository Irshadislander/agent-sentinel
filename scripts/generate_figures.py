from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

DEFAULT_INPUT_PATH = Path("bench/results/day12_aggregate.json")
DEFAULT_OUT_DIR = Path("paper/figures")


def _load_groups(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    groups = payload.get("groups") if isinstance(payload, dict) else None
    if not isinstance(groups, list):
        return []
    return [group for group in groups if isinstance(group, dict)]


def _group_key(group: dict[str, Any]) -> tuple[str, str]:
    return str(group.get("baseline", "unknown")), str(group.get("scenario_id", "default"))


def _metrics(group: dict[str, Any]) -> dict[str, float]:
    metrics = group.get("metrics", {})
    if not isinstance(metrics, dict):
        return {}
    return {str(k): float(v) for k, v in metrics.items()}


def _figure_baselines_mean_std(groups: list[dict[str, Any]], out_path: Path, plt: Any) -> None:
    default_scenario_groups = [
        group for group in groups if str(group.get("scenario_id", "")) == "default"
    ]
    chosen = default_scenario_groups if default_scenario_groups else groups

    by_baseline: dict[str, dict[str, float]] = {}
    for group in chosen:
        baseline = str(group.get("baseline", "unknown"))
        by_baseline[baseline] = _metrics(group)

    baselines = sorted(by_baseline)
    uer_mean = [by_baseline[b].get("uer_mean", 0.0) for b in baselines]
    uer_std = [by_baseline[b].get("uer_std", 0.0) for b in baselines]
    far_mean = [by_baseline[b].get("far_mean", 0.0) for b in baselines]
    far_std = [by_baseline[b].get("far_std", 0.0) for b in baselines]
    tcr_mean = [by_baseline[b].get("tcr_mean", 0.0) for b in baselines]
    tcr_std = [by_baseline[b].get("tcr_std", 0.0) for b in baselines]

    width = 0.25
    positions = list(range(len(baselines)))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(
        [p - width for p in positions], uer_mean, width=width, yerr=uer_std, capsize=3, label="UER"
    )
    ax.bar(positions, far_mean, width=width, yerr=far_std, capsize=3, label="FAR")
    ax.bar(
        [p + width for p in positions], tcr_mean, width=width, yerr=tcr_std, capsize=3, label="TCR"
    )
    ax.set_xticks(positions)
    ax.set_xticklabels(baselines, rotation=20, ha="right")
    ax.set_ylim(0.0, 1.05)
    ax.set_ylabel("Metric value")
    ax.set_title("Baselines (mean ± std)")
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def _figure_trace_tradeoff(groups: list[dict[str, Any]], out_path: Path, plt: Any) -> None:
    points: list[tuple[float, float]] = []
    for group in groups:
        baseline = str(group.get("baseline", ""))
        scenario_id = str(group.get("scenario_id", ""))
        if baseline != "default":
            continue
        if scenario_id.startswith("sens_"):
            match = re.search(r"_trace=([0-9.]+)", scenario_id)
            if match:
                metrics = _metrics(group)
                points.append((float(match.group(1)), metrics.get("tcr_mean", 0.0)))

    if not points:
        for group in groups:
            if str(group.get("baseline", "")) == "default":
                metrics = _metrics(group)
                points.append((1.0, metrics.get("tcr_mean", 0.0)))

    points = sorted(points, key=lambda item: item[0])
    x_values = [p[0] for p in points]
    y_values = [p[1] for p in points]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x_values, y_values, marker="o")
    ax.set_xlabel("Trace sample rate")
    ax.set_ylabel("TCR mean")
    ax.set_ylim(0.0, 1.05)
    ax.set_title("Trace Sampling Tradeoff")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def _figure_latency_tradeoff(groups: list[dict[str, Any]], out_path: Path, plt: Any) -> None:
    points: list[tuple[float, float, str]] = []
    for group in groups:
        metrics = _metrics(group)
        uer = metrics.get("uer_mean", 0.0)
        p95 = metrics.get("latency_p95_ms_mean", 0.0)
        label = f"{group.get('baseline', 'unknown')}|{group.get('scenario_id', 'default')}"
        points.append((uer, p95, label))

    fig, ax = plt.subplots(figsize=(9, 5))
    for uer, p95, label in points:
        ax.scatter([uer], [p95], s=45)
        ax.annotate(label, (uer, p95), textcoords="offset points", xytext=(4, 4), fontsize=8)
    ax.set_xlabel("UER mean")
    ax.set_ylabel("Latency p95 mean (ms)")
    ax.set_title("Latency Tradeoff")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate day12 paper figures from aggregate metrics."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT_PATH),
        help=f"Aggregate input JSON path (default: {DEFAULT_INPUT_PATH})",
    )
    parser.add_argument(
        "--out-dir",
        default=str(DEFAULT_OUT_DIR),
        help=f"Output directory for figures (default: {DEFAULT_OUT_DIR})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    out_dir = Path(args.out_dir)
    if not input_path.exists():
        raise SystemExit(f"aggregate input not found: {input_path}")

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover
        raise SystemExit(f"matplotlib is required for figure generation: {exc}") from exc

    groups = _load_groups(input_path)
    if not groups:
        raise SystemExit(f"no aggregate groups found in input: {input_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    fig1_path = out_dir / "fig_baselines_mean_std.png"
    fig2_path = out_dir / "fig_trace_tradeoff.png"
    fig3_path = out_dir / "fig_latency_tradeoff.png"

    _figure_baselines_mean_std(groups, fig1_path, plt)
    _figure_trace_tradeoff(groups, fig2_path, plt)
    _figure_latency_tradeoff(groups, fig3_path, plt)

    print(f"Wrote figure: {fig1_path}")
    print(f"Wrote figure: {fig2_path}")
    print(f"Wrote figure: {fig3_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
