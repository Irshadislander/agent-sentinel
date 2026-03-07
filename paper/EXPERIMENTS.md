# Experiments

## 1. Evaluation Scope
We evaluate deterministic runtime capability gating across three dimensions:
- security effectiveness,
- performance overhead and scaling,
- observability quality.

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

## 5. Core Execution Procedure
1. Load workloads from `configs/tasks/` and `configs/tasks_synth/`.
2. Partition workloads by family and difficulty.
3. Run each slice under each baseline.
4. Collect allow/deny outcomes, latency, throughput, and decision artifacts.
5. Compute metrics for each `(family, difficulty, baseline)` cell.
6. Aggregate outputs into report tables.

## 6. Performance Evaluation Setup
- Record CPU, RAM, OS/kernel, Python version, and git SHA.
- Keep runtime settings fixed within each comparison slice.
- Measure p50/p95/p99 latency, throughput, and overhead deltas versus reference.

## 7. Scale Experiments
Scale experiments evaluate larger task sets under unchanged policy semantics.

Suggested scale tiers:
- `small`, `medium`, `large`

Report:
- throughput per tier,
- p50/p95/p99 latency per tier,
- throughput and latency ratios versus smallest tier.

## 8. Stress Experiments
Stress experiments evaluate behavior under adverse conditions.

Examples:
- mixed-family bursts,
- elevated adversarial density,
- malformed request/context inputs,
- high deny-rate workloads.

Report:
- ABR/ASR stability,
- tail latency behavior,
- TCR/SDAC behavior under stress.

## 9. Sensitivity Experiments
Sensitivity experiments vary evaluation controls and policy/runtime knobs.

Examples:
- policy strictness settings,
- trace detail/integrity settings,
- capability-granularity settings.

Report:
- directional security changes,
- overhead/throughput sensitivity,
- observability sensitivity.

## 10. Overhead Interpretation Relative to Security Gains
Interpret overhead jointly with security and observability:
- compare latency/throughput deltas against ABR/ASR improvements,
- treat moderate overhead as acceptable when it yields clear risk reduction and stable traces,
- flag configurations with high overhead and weak security gain.

## 11. Metrics Reported
Primary metrics (see [METRICS](METRICS.md)):
- security: ABR, ASR,
- performance: p50/p95/p99 latency overhead, throughput, scaling behavior,
- observability: TCR, SDAC.

## 12. Statistical Reporting
- report mean and 95% confidence intervals,
- use identical workload slices across compared systems,
- keep artifact generation reproducible.
