# Experiments

## 1. Hardware and Runtime Environment

For each run set, report:

- CPU model and core count
- RAM
- OS/kernel string
- Python version
- Git commit SHA

Runtime assumptions:
- Python 3.11+
- package installed with dev dependencies: `pip install -e ".[dev]"`

## 2. Benchmark Structure
Core matrix:

\[
\text{ablation modes} \times \text{attack families} \times \text{difficulty levels} \times \text{metrics}
\]

This structure is used to isolate which removed/weakened component causes each degradation.

## 3. Ablation Modes
1. `full_system` (reference mode).
2. `no_default_deny`.
3. `no_first_match_ordering`.
4. `no_trace` / `reduced_observability`.
5. `no_capability_confinement` / `coarse_capability_gating`.
6. `no_enforcement`.

What each mode is meant to show:
- `no_default_deny`: effect of removing deny fallback for unmatched cases.
- `no_first_match_ordering`: effect of removing deterministic rule conflict resolution.
- `no_trace`: effect of reducing observability and audit evidence.
- `no_capability_confinement`: effect of weakening fine-grained least-privilege boundaries.
- `no_enforcement`: lower-bound safety when enforcement is bypassed entirely.

If a mode is not yet implemented in the current benchmark runner, mark it as planned and keep its reporting row as placeholder.

## 4. Workload Axes
### Attack families
- `prompt_injection`
- `filesystem_damage`
- `shell_misuse`
- `data_exfiltration`
- `network_exfiltration`

### Difficulty
- `easy`
- `medium`
- `hard` / `multi_step`

## 5. Evaluation Workflow
1. Load workload tasks from `configs/tasks/` and `configs/tasks_synth/`.
2. Execute each task under a selected system mode (baseline/ablation).
3. Apply policy enforcement at runtime decision boundary.
4. Capture trace and structured decision artifacts.
5. Compute metrics by system, family, and difficulty.
6. Export artifacts and paper tables.

## 6. Attack Execution Procedure
- Run all tasks in each `(family, difficulty)` slice through the same runtime path.
- Keep policy inputs and run settings fixed within each comparison slice.
- Record allow/deny outcomes, latency, and decision artifact fields for every request.
- Repeat runs across seeds when available.

## 7. Baseline Evaluation Procedure
Evaluate `default` and baseline/ablation modes against identical workloads.

For each mode:
- run the same workload matrix,
- compute the same metric set,
- compare with reference (`default` for baseline tables, `full_system` for ablation tables).

## 8. Metrics and Reporting
Use the primary metrics in [METRICS](METRICS.md):
- attack block rate,
- latency overhead,
- trace completeness,
- structured decision artifact coverage.

Reporting slices:
- per-ablation aggregate,
- per-family,
- per-family x difficulty,
- deltas versus `full_system`.

## 9. Ablation Reporting Plan
For each ablation mode, report:
- component removed/weakened,
- expected failure mode,
- observed deltas on primary metrics:
  attack block rate, latency overhead, trace completeness, structured artifact coverage.

Use:
\[
\Delta m = m(\text{ablation}) - m(\text{full\_system})
\]

## 10. Repetition and Statistics
- Run repeated trials (minimum 10 when available).
- Report mean and spread (std and/or CI when available).
- Preserve run metadata (`git SHA`, runtime config, timestamp) for reproducibility.
