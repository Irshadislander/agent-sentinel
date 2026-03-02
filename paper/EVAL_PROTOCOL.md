# Evaluation Protocol

## 1. Task Set
Tasks are sourced from `configs/tasks/` and grouped by evaluation category:
- `benign`
- `policy_blocked`
- `malformed_payload`
- `plugin_failure`
- `trace_stress`

The category labels define expected behavioral classes for policy and error analysis.

## 2. Baselines
### B0 (default)
Full system enabled: policy enforcement, tracing, and structured errors.

### B1 (no_policy)
Policy gate bypassed; capability requests are allowed by the benchmark execution path while tracing remains enabled.

### B2 (no_trace)
Tracing disabled; execution still uses policy and structured errors.

### B3 (raw_errors)
Structured error taxonomy disabled at benchmark boundary; failures are represented as raw exception strings.

### B4 (no_plugin_isolation)
Plugin isolation disabled; discovered plugins are treated as unrestricted (no allowlist enforcement).

## 3. Metrics
Primary metrics are defined in `paper/METRICS.md`:
- UER
- FAR
- TCR
- EDS
- PEA

Mapping to `bench/results/matrix.json` fields:
- `baseline`, `task_id`, `category`, `decision`
- `exit_code`, `duration_ms`
- `has_trace`
- `error_kind`, `raw_error`

## 4. Experimental Procedure
1. Fix task set from `configs/tasks/`.
2. Run matrix with baseline controls:
   - `python -m agent_sentinel.benchmark.run_benchmark --matrix --matrix-all-baselines`
3. Repeat matrix runs \(N\) times (default \(N=10\)) for determinism-sensitive statistics.
4. Report mean and standard deviation across runs.

## 5. Reproducibility Checklist
- Record exact commands and argument values.
- Capture CI artifacts:
  - `bench/results/matrix.json`
  - `bench/results/matrix.csv`
  - `docs/bench_report.md`
- Record commit SHA and timestamp.
- If randomness is introduced, pin seeds and report them explicitly.
