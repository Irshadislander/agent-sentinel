# Reproducibility

This document defines a deterministic baseline workflow for benchmark and paper artifacts.

## Environment Capture

Run:

```bash
python3 -VV
uname -a
git rev-parse --short HEAD
```

Record:
- Python version
- OS/kernel string
- Git commit SHA

## Deterministic Benchmark Commands

From repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

### 1) Matrix Benchmark (fixed output filenames)

```bash
python -m agent_sentinel.benchmark.run_benchmark \
  --matrix \
  --matrix-all-baselines \
  --output-dir artifacts/bench
```

Expected files:
- `artifacts/bench/matrix.json`
- `artifacts/bench/matrix.csv`

### 2) Single Baseline Benchmark (fixed output filenames)

```bash
python -m agent_sentinel.benchmark.run_benchmark \
  --baseline default \
  --output-dir artifacts/bench \
  --json-name latest.json \
  --csv-name latest.csv
```

Expected files:
- `artifacts/bench/latest.json`
- `artifacts/bench/latest.csv`

### 3) Policy-Engine Microbenchmark (fixed output filenames)

```bash
python scripts/bench_policy_engine.py
```

Expected files:
- `artifacts/bench/policy_engine_bench.json`
- `paper/PERF_DAYXX.md`

### 4) Canonical Report Bundle

```bash
python scripts/generate_canonical_report.py \
  --matrix-input artifacts/bench/matrix.json \
  --results-output paper/results_tables.md \
  --policy-perf-json artifacts/bench/policy_engine_bench.json \
  --policy-perf-markdown paper/PERF_DAYXX.md \
  --robustness-output artifacts/bench/robustness_report.json
```

Expected files:
- `paper/results_tables.md`
- `artifacts/bench/policy_engine_bench.json`
- `artifacts/bench/robustness_report.json`
- `paper/PERF_DAYXX.md`

## Expected CLI Confirmation Strings

- Benchmark run: `Benchmark results written: ...`
- Matrix run: `Benchmark matrix written: ...`
- Policy microbenchmark: `Wrote policy engine benchmark JSON: ...`
- Canonical report: `Wrote results summary markdown: ...`

## Notes

- Output filenames under `artifacts/bench/` are deterministic (`latest.*`, `matrix.*`, `policy_engine_bench.json`, `robustness_report.json`).
- Timestamps and benchmark IDs inside JSON payloads are expected to vary by run.
