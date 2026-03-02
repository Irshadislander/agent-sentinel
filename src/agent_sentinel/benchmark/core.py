from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from time import perf_counter_ns


@dataclass(frozen=True)
class BenchmarkResult:
    iterations: int
    avg_ms: float
    min_ms: float
    max_ms: float


def run_benchmark(fn: Callable[[], None], *, iterations: int, warmup: int = 0) -> BenchmarkResult:
    """
    Deterministic micro-benchmark runner.

    - Uses perf_counter_ns (monotonic high resolution)
    - No external deps (no pytest-benchmark)
    - Returns stable structured results
    """
    if iterations <= 0:
        raise ValueError("iterations must be > 0")
    if warmup < 0:
        raise ValueError("warmup must be >= 0")

    # Warmup
    for _ in range(warmup):
        fn()

    min_ns = None
    max_ns = None
    total_ns = 0

    for _ in range(iterations):
        start = perf_counter_ns()
        fn()
        elapsed = perf_counter_ns() - start

        total_ns += elapsed
        min_ns = elapsed if min_ns is None else min(min_ns, elapsed)
        max_ns = elapsed if max_ns is None else max(max_ns, elapsed)

    assert min_ns is not None and max_ns is not None

    avg_ms = (total_ns / iterations) / 1_000_000
    min_ms = min_ns / 1_000_000
    max_ms = max_ns / 1_000_000

    return BenchmarkResult(iterations=iterations, avg_ms=avg_ms, min_ms=min_ms, max_ms=max_ms)
