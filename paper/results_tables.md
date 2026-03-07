# Paper Result Tables

Populate all entries from measured artifacts only.

## Overall Performance Summary

Related figure: **Security–Performance Tradeoff** (`paper/figures/fig_security_performance_tradeoff.png` or `paper/figures/fig_pareto_frontier.png`).

| System/Baseline | Security summary (ABR/ASR) | Performance summary (latency + throughput) | Observability summary (TCR/SDAC) | Overall interpretation |
|---|---|---|---|---|
| `full_system` | `TBD` | `TBD` | `TBD` | reference |
| `no_enforcement` | `TBD` | `TBD` | `TBD` | `TBD` |
| `allow_all` | `TBD` | `TBD` | `TBD` | `TBD` |
| `naive_allow_list` | `TBD` | `TBD` | `TBD` | `TBD` |
| `llm_guard_style` (optional/future) | `TBD/NA` | `TBD/NA` | `TBD/NA` | `NA` if unavailable |

## Latency and Overhead

Reference: `full_system`
Related figure: **Security–Performance Tradeoff** (`paper/figures/fig_security_performance_tradeoff.png` or `paper/figures/fig_pareto_frontier.png`).

| Baseline | p50 latency (mean, 95% CI) | p95 latency (mean, 95% CI) | p99 latency (mean, 95% CI) | Δp50 | Δp95 | Δp99 | Throughput (mean, 95% CI) |
|---|---|---|---|---|---|---|---|
| `full_system` | `TBD` | `TBD` | `TBD` | `0` | `0` | `0` | `TBD` |
| `no_enforcement` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `allow_all` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `naive_allow_list` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `llm_guard_style` (optional/future) | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` |

## Scaling Results

Related figure: **Scaling Curve** (`paper/figures/fig_scaling_curve.png`).

| Scale tier | Workload size | Baseline | Throughput (mean, 95% CI) | p95 latency (mean, 95% CI) | Throughput ratio vs smallest | p95 ratio vs smallest | Notes |
|---|---:|---|---|---|---|---|---|
| `small` | `TBD` | `TBD` | `TBD` | `TBD` | `1.0` | `1.0` | `TBD` |
| `medium` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `large` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## Stress / Sensitivity Summary

Related figure: stress/sensitivity overlays when available; otherwise interpret with the tradeoff figure.

| Condition type | Condition | Baseline | ABR | ASR | p95 latency | Throughput | TCR | SDAC | Interpretation |
|---|---|---|---|---|---|---|---|---|---|
| `stress` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `sensitivity` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## Security–Performance Tradeoff Summary

Related figure: **Security–Performance Tradeoff** (`paper/figures/fig_security_performance_tradeoff.png` or `paper/figures/fig_pareto_frontier.png`).

| Baseline | Security delta vs `full_system` (ABR/ASR) | Performance delta vs `full_system` (latency/throughput) | Observability delta (TCR/SDAC) | Tradeoff assessment |
|---|---|---|---|---|
| `no_enforcement` | `TBD` | `TBD` | `TBD` | `TBD` |
| `allow_all` | `TBD` | `TBD` | `TBD` | `TBD` |
| `naive_allow_list` | `TBD` | `TBD` | `TBD` | `TBD` |
| `llm_guard_style` (optional/future) | `TBD/NA` | `TBD/NA` | `TBD/NA` | `NA` if unavailable |

## Notes

- Do not insert synthetic values.
- Keep optional/future baseline rows as `NA` when unavailable.
- Use identical workload slices for valid tradeoff comparisons.
- Family-level rows map to **Attack Family Blocking Summary** (`paper/figures/fig_attack_family_blocking_summary.png`).
