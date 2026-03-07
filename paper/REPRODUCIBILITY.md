# Reproducibility

This document provides an artifact-evaluation-ready procedure for reproducing Agent-Sentinel evaluation outputs from a clean checkout.

## 1) Required Environment

- OS: Linux or macOS
- Python: **3.11+** (`pyproject.toml` requires `>=3.11`)
- Tools: `git`, `python3`, `pip`, shell

Record environment metadata:

```bash
python3 -VV
uname -a
git rev-parse --short HEAD
```

## 2) Dependency Installation

From repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

## 3) Test Execution

```bash
pytest -q
```

## 4) Benchmark Execution Steps

### 4.1 Matrix benchmark

```bash
python -m agent_sentinel.benchmark.run_benchmark \
  --matrix \
  --matrix-all-baselines \
  --output-dir artifacts/bench
```

Expected outputs:
- `artifacts/bench/matrix.json`
- `artifacts/bench/matrix.csv`

### 4.2 Single baseline sanity run

```bash
python -m agent_sentinel.benchmark.run_benchmark \
  --baseline default \
  --output-dir artifacts/bench \
  --json-name latest.json \
  --csv-name latest.csv
```

Expected outputs:
- `artifacts/bench/latest.json`
- `artifacts/bench/latest.csv`

### 4.3 Policy-engine microbenchmark

```bash
python scripts/bench_policy_engine.py
```

Expected output:
- `artifacts/bench/policy_engine_bench.json`

## 5) Result Table Generation

```bash
python scripts/generate_canonical_report.py \
  --matrix-input artifacts/bench/matrix.json \
  --results-output paper/results_tables.md \
  --policy-perf-json artifacts/bench/policy_engine_bench.json \
  --policy-perf-markdown paper/PERF_DAYXX.md \
  --robustness-output artifacts/bench/robustness_report.json
```

Expected outputs:
- `paper/results_tables.md`
- `paper/PERF_DAYXX.md`
- `artifacts/bench/robustness_report.json`

## 6) Where Evaluation Inputs Are Defined

- Attack scenarios / workloads:
  - `configs/tasks/`
  - `configs/tasks_synth/`
  - framing: `paper/ATTACK_SCENARIOS.md`
- Policies:
  - `configs/policies/default.yaml`
  - enforcement logic: `src/agent_sentinel/security/policy_engine.py`

## 7) Determinism Notes

- Output filenames under `artifacts/bench/` are deterministic (`matrix.*`, `latest.*`, `policy_engine_bench.json`, `robustness_report.json`).
- Timestamps and run identifiers inside output JSON are expected to vary.
- Statistical reporting conventions are documented in `paper/APPENDIX_STATS.md`.
