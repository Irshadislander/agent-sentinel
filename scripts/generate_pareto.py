from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_INPUT_PATH = Path("bench/results/day12_aggregate.json")
DEFAULT_OUTPUT_DIR = Path("paper/figures")
DEFAULT_ANALYSIS_PATH = Path("paper/PARETO_ANALYSIS.md")


@dataclass(frozen=True)
class BaselinePoint:
    baseline: str
    safety: float
    latency: float
    trace: float


def _load_groups(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    groups = payload.get("groups") if isinstance(payload, dict) else None
    if not isinstance(groups, list):
        return []
    return [group for group in groups if isinstance(group, dict)]


def _extract_points(groups: list[dict[str, Any]]) -> list[BaselinePoint]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for group in groups:
        baseline = str(group.get("baseline", "")).strip()
        if not baseline:
            continue
        grouped.setdefault(baseline, []).append(group)

    points: list[BaselinePoint] = []
    for baseline in sorted(grouped):
        entries = grouped[baseline]

        # Prefer scenario_id=default if present, otherwise average across scenarios.
        default_entry = next(
            (entry for entry in entries if str(entry.get("scenario_id", "")).strip() == "default"),
            None,
        )
        chosen_entries = [default_entry] if default_entry is not None else entries

        safety_values: list[float] = []
        latency_values: list[float] = []
        trace_values: list[float] = []
        for entry in chosen_entries:
            metrics = entry.get("metrics", {})
            if not isinstance(metrics, dict):
                continue
            uer = float(metrics.get("uer_mean", 0.0))
            safety_values.append(1.0 - uer)
            latency_values.append(float(metrics.get("latency_p95_ms_mean", 0.0)))
            trace_values.append(float(metrics.get("tcr_mean", 0.0)))

        if not safety_values:
            continue
        points.append(
            BaselinePoint(
                baseline=baseline,
                safety=sum(safety_values) / len(safety_values),
                latency=sum(latency_values) / len(latency_values),
                trace=sum(trace_values) / len(trace_values),
            )
        )

    return points


def _dominates(a: BaselinePoint, b: BaselinePoint) -> bool:
    better_or_equal = (a.safety >= b.safety) and (a.latency <= b.latency)
    strictly_better = (a.safety > b.safety) or (a.latency < b.latency)
    return better_or_equal and strictly_better


def _pareto_points(points: list[BaselinePoint]) -> list[BaselinePoint]:
    frontier: list[BaselinePoint] = []
    for point in points:
        dominated = False
        for other in points:
            if other is point:
                continue
            if _dominates(other, point):
                dominated = True
                break
        if not dominated:
            frontier.append(point)
    return sorted(frontier, key=lambda p: (p.latency, -p.safety, p.baseline))


def _write_analysis(path: Path, points: list[BaselinePoint], frontier: list[BaselinePoint]) -> None:
    lines: list[str] = [
        "# Pareto Analysis",
        "",
        "Safety is defined as `1 - UER_mean`; latency uses `latency_p95_mean`; trace uses `TCR_mean`.",
        "",
        "## Points",
        "",
        "| baseline | latency_p95_mean | safety (1-UER_mean) | trace (TCR_mean) | pareto |",
        "|---|---:|---:|---:|---:|",
    ]

    frontier_names = {point.baseline for point in frontier}
    for point in sorted(points, key=lambda p: (p.latency, -p.safety, p.baseline)):
        lines.append(
            f"| {point.baseline} | {point.latency:.3f} | {point.safety:.4f} | "
            f"{point.trace:.4f} | {'yes' if point.baseline in frontier_names else 'no'} |"
        )

    lines.extend(["", "## Pareto Frontier", ""])
    if frontier:
        for point in frontier:
            lines.append(
                f"- `{point.baseline}`: latency={point.latency:.3f}, "
                f"safety={point.safety:.4f}, trace={point.trace:.4f}"
            )
    else:
        lines.append("- No points available.")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _plot(points: list[BaselinePoint], frontier: list[BaselinePoint], output_path: Path) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover
        raise SystemExit(f"matplotlib is required for pareto plotting: {exc}") from exc

    x = [point.latency for point in points]
    y = [point.safety for point in points]
    c = [point.trace for point in points]

    fig, ax = plt.subplots(figsize=(8, 5))
    scatter = ax.scatter(x, y, c=c, cmap="viridis", s=65, alpha=0.9, edgecolors="black")

    frontier_names = {point.baseline for point in frontier}
    for point in points:
        marker_size = 140 if point.baseline in frontier_names else 65
        edge_width = 2.0 if point.baseline in frontier_names else 0.8
        ax.scatter(
            [point.latency],
            [point.safety],
            c=[point.trace],
            cmap="viridis",
            s=marker_size,
            edgecolors="black",
            linewidths=edge_width,
        )
        ax.annotate(
            point.baseline,
            (point.latency, point.safety),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=8,
        )

    if frontier:
        fx = [point.latency for point in frontier]
        fy = [point.safety for point in frontier]
        ax.plot(fx, fy, linestyle="--", linewidth=1.5, color="black", alpha=0.7)

    ax.set_xlabel("Latency p95 mean (ms)")
    ax.set_ylabel("Safety score (1 - UER mean)")
    ax.set_title("Pareto Frontier: Safety vs Latency (color = TCR mean)")
    ax.grid(True, alpha=0.3)
    colorbar = fig.colorbar(scatter, ax=ax)
    colorbar.set_label("TCR mean")
    fig.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate Pareto frontier plot for day12 aggregate."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT_PATH),
        help=f"Input aggregate JSON path (default: {DEFAULT_INPUT_PATH})",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output figure directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    output_dir = Path(args.out)
    if not input_path.exists():
        raise SystemExit(f"input not found: {input_path}")

    groups = _load_groups(input_path)
    if not groups:
        raise SystemExit(f"no groups found in aggregate input: {input_path}")

    points = _extract_points(groups)
    frontier = _pareto_points(points)

    figure_path = output_dir / "fig_pareto_frontier.png"
    _plot(points, frontier, figure_path)
    _write_analysis(DEFAULT_ANALYSIS_PATH, points, frontier)

    print(f"Wrote figure: {figure_path}")
    print(f"Wrote analysis: {DEFAULT_ANALYSIS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
