from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ModuleNotFoundError as exc:
    raise SystemExit(f"matplotlib is required for figure generation: {exc}") from exc

DEFAULT_INPUT_PATH = Path("artifacts/baselines/baseline_suite.json")
DEFAULT_LATENCY_FIG_PATH = Path("paper/figures/fig_baseline_block_vs_latency.png")
DEFAULT_SAFETY_FIG_PATH = Path("paper/figures/fig_baseline_safe_vs_unsafe.png")
DISPLAY_ORDER = [
    "No Protection",
    "Static Allowlist",
    "Argument Allowlist",
    "Validator Only",
    "No Audit",
    "Progent-style",
    "Agent-Sentinel",
]


def _load_systems(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("baseline suite payload must be a JSON object")
    systems = payload.get("systems", [])
    if not isinstance(systems, list):
        raise ValueError("baseline suite payload missing systems list")
    by_label = {
        str(system.get("label", "")): system for system in systems if isinstance(system, dict)
    }
    return [by_label[label] for label in DISPLAY_ORDER if label in by_label]


def _metric(system: dict[str, Any], key: str) -> float:
    try:
        return float(system.get(key, 0.0))
    except (TypeError, ValueError):
        return 0.0


def _annotate_points(ax: Any, xs: list[float], ys: list[float], labels: list[str]) -> None:
    for x_value, y_value, label in zip(xs, ys, labels, strict=True):
        ax.annotate(
            label, (x_value, y_value), xytext=(5, 5), textcoords="offset points", fontsize=9
        )


def generate_figures(
    *,
    input_path: Path = DEFAULT_INPUT_PATH,
    latency_fig_path: Path = DEFAULT_LATENCY_FIG_PATH,
    safety_fig_path: Path = DEFAULT_SAFETY_FIG_PATH,
) -> tuple[Path, Path]:
    systems = _load_systems(input_path)
    labels = [str(system.get("label", "")) for system in systems]

    unsafe_blocked = [_metric(system, "unsafe_actions_blocked_pct") for system in systems]
    safe_allowed = [_metric(system, "safe_actions_allowed_pct") for system in systems]
    median_latency = [_metric(system, "median_latency_ms") for system in systems]

    latency_fig_path.parent.mkdir(parents=True, exist_ok=True)
    safety_fig_path.parent.mkdir(parents=True, exist_ok=True)

    figure, axis = plt.subplots(figsize=(6.0, 4.0))
    axis.scatter(median_latency, unsafe_blocked, color="black", s=35)
    axis.set_xlabel("Median Latency (ms)")
    axis.set_ylabel("Unsafe Actions Blocked (%)")
    axis.set_title("Baseline Blocking vs. Latency")
    axis.grid(True, linewidth=0.4, alpha=0.4)
    _annotate_points(axis, median_latency, unsafe_blocked, labels)
    figure.tight_layout()
    figure.savefig(latency_fig_path, dpi=300)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(6.0, 4.0))
    axis.scatter(unsafe_blocked, safe_allowed, color="black", s=35)
    axis.set_xlabel("Unsafe Actions Blocked (%)")
    axis.set_ylabel("Safe Actions Allowed (%)")
    axis.set_title("Safety Tradeoff Across Baselines")
    axis.grid(True, linewidth=0.4, alpha=0.4)
    _annotate_points(axis, unsafe_blocked, safe_allowed, labels)
    figure.tight_layout()
    figure.savefig(safety_fig_path, dpi=300)
    plt.close(figure)

    return latency_fig_path, safety_fig_path


def main() -> int:
    latency_fig_path, safety_fig_path = generate_figures()
    print(f"Baseline latency figure: {latency_fig_path}")
    print(f"Baseline safety figure: {safety_fig_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
