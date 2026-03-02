# Experiments

## 1. Experimental Setup
- Hardware: report CPU model, core count, and RAM for each run set.
- Python version: record `python --version` used to execute the benchmark.
- Number of tasks: use the fixed task set in `configs/tasks/`.
- Baseline flags: run `default`, `no_policy`, `no_trace`, `raw_errors`, and `no_plugin_isolation`.

## 2. Task Categories
Tasks are grouped into the following categories:
- `benign`
- `policy_blocked`
- `malformed_payload`
- `plugin_failure`
- `trace_stress`

## 3. Metrics Reporting Protocol
- Report mean and standard deviation for per-baseline metrics.
- Report latency using p50 and p95 per baseline and by category when available.
- Keep run metadata with timestamp, git SHA, and baseline configuration.

## 4. Statistical Reporting Plan
- Run at least 10 repeated executions for determinism-focused metrics.
- Use paired baseline comparisons against `default`.
- Report effect direction for each hypothesis (improvement vs degradation).
