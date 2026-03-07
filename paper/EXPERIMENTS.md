# Experiments

## 1. Evaluation Scope
We evaluate deterministic runtime capability gating under adversarial workloads and quantify:
- security effectiveness,
- observability quality,
- runtime overhead.

## 2. Systems Compared
### Reference
- `full_system`

### Baselines
- `no_enforcement`
- `allow_all`
- `naive_allow_list`
- `llm_guard_style` (optional/future unless implemented)

Unimplemented optional baselines are reported as `NA`.

## 3. Benchmark Matrix
\[
\text{attack family} \times \text{difficulty level} \times \text{baseline} \times \text{metric}
\]

This matrix defines the complete comparison space for baseline reporting.

## 4. Workload Axes
### Attack families
- `prompt_injection`
- `filesystem_damage`
- `shell_misuse`
- `data_exfiltration`
- `network_exfiltration`

### Difficulty levels
- `easy`
- `medium`
- `hard` / `multi_step`

## 5. Execution Procedure
1. Load workloads from `configs/tasks/` and `configs/tasks_synth/`.
2. Partition workloads by family and difficulty.
3. Run each slice under each baseline.
4. Collect allow/deny outcomes, latency, and decision artifacts.
5. Compute metrics for each `(family, difficulty, baseline)` cell.
6. Aggregate outputs into paper tables.

## 6. Metrics Reported
Primary metrics (see [METRICS](METRICS.md)):
- attack block rate,
- attack success rate,
- latency overhead,
- trace completeness,
- decision artifact / explainability coverage.

## 7. Reporting Structure
The paper reports:
- Overall Baseline Comparison,
- Attack Family Summary,
- Difficulty-Level Summary,
- Family × Difficulty Comparison,
- Per-Family Baseline Comparison,
- Overhead Comparison.

## 8. Runtime Metadata
For each run set, report:
- CPU,
- RAM,
- OS/kernel,
- Python version,
- git SHA.

## 9. Statistical Reporting
- Report mean and confidence intervals.
- Keep identical workload slices across baselines for valid deltas.
- Keep artifact generation reproducible.
