# Statistical Tables

Use this file to report baseline statistical comparisons from measured runs only.

## Baseline Deltas

Reference: `full_system`

| Baseline | Metric | Estimate | 95% CI | Delta vs `full_system` | 95% CI of delta | Interpretation |
|---|---|---|---|---|---|---|
| `no_enforcement` | ABR | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_enforcement` | ASR | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_enforcement` | TCR | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_enforcement` | SDAC | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `allow_all` | ABR | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `allow_all` | ASR | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `allow_all` | TCR | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `allow_all` | SDAC | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `naive_allow_list` | ABR | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `naive_allow_list` | ASR | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `naive_allow_list` | TCR | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `naive_allow_list` | SDAC | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `llm_guard_style` (optional/future) | ABR | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | mark `NA` if unavailable |

## Confidence Intervals by Baseline

| Baseline | ABR (95% CI) | ASR (95% CI) | p50 latency (95% CI) | p95 latency (95% CI) | p99 latency (95% CI) | TCR (95% CI) | SDAC (95% CI) |
|---|---|---|---|---|---|---|---|
| `full_system` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_enforcement` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `allow_all` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `naive_allow_list` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `llm_guard_style` (optional/future) | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` |

## Summary Comparisons Across Baselines

| Baseline | Security summary (ABR/ASR) | Overhead summary | Trace summary (TCR/SDAC) | Reviewer-facing interpretation |
|---|---|---|---|---|
| `full_system` | `TBD` | `TBD` | `TBD` | reference |
| `no_enforcement` | `TBD` | `TBD` | `TBD` | `TBD` |
| `allow_all` | `TBD` | `TBD` | `TBD` | `TBD` |
| `naive_allow_list` | `TBD` | `TBD` | `TBD` | `TBD` |
| `llm_guard_style` (optional/future) | `TBD/NA` | `TBD/NA` | `TBD/NA` | optional/future |

## Notes

- Use identical workload slices across baselines before computing deltas.
- Declare CI method once (bootstrap or analytic) and apply consistently.
- Do not report values for unimplemented optional baselines; use `NA`.
