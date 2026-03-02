import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_sentinel.benchmark.core import run_benchmark


def test_run_benchmark_counts_iterations():
    counter = {"n": 0}

    def fn():
        counter["n"] += 1

    result = run_benchmark(fn, iterations=50, warmup=10)

    assert counter["n"] == 60  # 50 + 10 warmup
    assert result.iterations == 50
    assert result.avg_ms >= 0.0
    assert result.min_ms >= 0.0
    assert result.max_ms >= 0.0


def test_run_benchmark_rejects_invalid_iterations():
    with pytest.raises(ValueError):
        run_benchmark(lambda: None, iterations=0)
