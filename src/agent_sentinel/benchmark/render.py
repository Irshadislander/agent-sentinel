from __future__ import annotations

import json
from dataclasses import asdict

from .core import BenchmarkResult


def render_benchmark(result: BenchmarkResult, *, as_json: bool) -> str:
    if as_json:
        return json.dumps(asdict(result), indent=2, sort_keys=True)

    return (
        "Policy enforcement benchmark\n"
        f"Iterations: {result.iterations}\n"
        f"Average: {result.avg_ms:.6f} ms\n"
        f"Min: {result.min_ms:.6f} ms\n"
        f"Max: {result.max_ms:.6f} ms"
    )
