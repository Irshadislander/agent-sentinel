# Statistical Tables

Populate all entries from measured runs only.

## Confidence Interval Reporting for Performance Results

| Metric | Estimate | 95% CI | Reference | Delta vs reference | 95% CI of delta |
|---|---|---|---|---|---|
| p50 latency | `TBD` | `TBD` | `full_system` | `TBD` | `TBD` |
| p95 latency | `TBD` | `TBD` | `full_system` | `TBD` | `TBD` |
| p99 latency | `TBD` | `TBD` | `full_system` | `TBD` | `TBD` |
| throughput | `TBD` | `TBD` | `full_system` | `TBD` | `TBD` |

## Latency Summary Tables

| Baseline | p50 (mean, 95% CI) | p95 (mean, 95% CI) | p99 (mean, 95% CI) | Δp50 | Δp95 | Δp99 |
|---|---|---|---|---|---|---|
| `full_system` | `TBD` | `TBD` | `TBD` | `0` | `0` | `0` |
| `no_enforcement` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `allow_all` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `naive_allow_list` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `llm_guard_style` (optional/future) | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` |

## Scale Summary Tables

| Scale tier | Workload size | Baseline | Throughput (mean, 95% CI) | p95 latency (mean, 95% CI) | Throughput ratio vs smallest | p95 ratio vs smallest |
|---|---:|---|---|---|---|---|
| `small` | `TBD` | `TBD` | `TBD` | `TBD` | `1.0` | `1.0` |
| `medium` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `large` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## Stress Summary Tables

| Stress condition | Baseline | ABR (mean, 95% CI) | ASR (mean, 95% CI) | p95 latency (mean, 95% CI) | Throughput (mean, 95% CI) | TCR (mean, 95% CI) |
|---|---|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## Sensitivity Summary Tables

| Sensitivity knob | Setting | Baseline | ABR | ASR | p95 latency | Throughput | TCR | SDAC |
|---|---|---|---|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## Notes

- Declare one CI method and apply it consistently.
- Use identical workload slices and environment controls for delta reporting.
- Report optional/future baselines as `NA` when unavailable.
