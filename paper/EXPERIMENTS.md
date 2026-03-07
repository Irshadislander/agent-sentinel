# Experiments

## 1. Benchmark Structure
Core matrix:

\[
\text{systems} \times \text{attack families} \times \text{difficulty levels} \times \text{metrics}
\]

This structure is used to separate workload difficulty effects from system design effects.

## 2. Systems / Baseline Conditions
1. `default` (Agent-Sentinel full runtime enforcement).
2. no enforcement (`no_policy` / `no_gateway_enforcement` mode).
3. allow-all policy condition.
4. naive allow-list condition.
5. optional LLM-guard style baseline (future/optional if not implemented in current runner).

What each baseline shows:
- no enforcement: lower-bound safety behavior when gating is removed.
- allow-all: policy permissiveness effect.
- naive allow-list: gap between basic allow-listing and structured runtime enforcement.
- optional LLM guard: prompt-side probabilistic filtering versus deterministic runtime gating.

## 3. Workload Axes
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

## 4. Metrics and Reporting
Use the primary metrics in [METRICS](METRICS.md):
- attack block rate,
- latency overhead,
- trace completeness,
- structured decision artifact coverage.

Reporting slices:
- per-system aggregate,
- per-family,
- per-family x difficulty,
- deltas versus `default`.

## 5. Repetition and Statistics
- Run repeated trials (minimum 10 when available).
- Report mean and spread (std and/or CI when available).
- Preserve run metadata (`git SHA`, runtime config, timestamp) for reproducibility.
