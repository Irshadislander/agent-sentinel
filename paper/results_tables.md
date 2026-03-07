# Paper Result Tables (Final Freeze)

All paper-facing tables are derived from benchmark aggregates (for example `matrix.json` / `matrix.csv` style summaries). Populate from measured outputs only.

## 1. Overall Baseline Comparison

Reference: `full_system`

| Baseline | ABR (mean, 95% CI) | ASR (mean, 95% CI) | TCR (mean, 95% CI) | SDAC (mean, 95% CI) | p95 latency overhead | Throughput | Notes |
|---|---|---|---|---|---|---|---|
| `full_system` | `TBD` | `TBD` | `TBD` | `TBD` | `0` | `TBD` | reference |
| `no_enforcement` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `allow_all` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `naive_allow_list` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `llm_guard_style` (optional/future) | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | `NA` if unavailable |

## 2. Attack Family Summary

| Attack family | ABR (mean, 95% CI) | ASR (mean, 95% CI) | TCR (mean, 95% CI) | SDAC (mean, 95% CI) | p95 latency (mean, 95% CI) |
|---|---|---|---|---|---|
| `prompt_injection` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `filesystem_damage` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `shell_misuse` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `data_exfiltration` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `network_exfiltration` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## 3. Difficulty-Level Summary

| Difficulty | ABR (mean, 95% CI) | ASR (mean, 95% CI) | TCR (mean, 95% CI) | SDAC (mean, 95% CI) | p95 latency (mean, 95% CI) |
|---|---|---|---|---|---|
| `easy` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `medium` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `hard` / `multi_step` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## 4. Security–Performance Summary

Reference: `full_system`

| Baseline | Security delta (ABR/ASR) | Performance delta (p50/p95/p99, throughput) | Observability delta (TCR/SDAC) | Summary interpretation |
|---|---|---|---|---|
| `no_enforcement` | `TBD` | `TBD` | `TBD` | `TBD` |
| `allow_all` | `TBD` | `TBD` | `TBD` | `TBD` |
| `naive_allow_list` | `TBD` | `TBD` | `TBD` | `TBD` |
| `llm_guard_style` (optional/future) | `TBD/NA` | `TBD/NA` | `TBD/NA` | `NA` if unavailable |

## 5. Ablation Summary

Reference: `full_system`

| Ablation mode | Component changed | ABR / ASR impact | TCR / SDAC impact | Performance impact | Notes |
|---|---|---|---|---|---|
| `no_default_deny` | default-deny behavior weakened | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_first_match_ordering` | deterministic first-match ordering removed | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_trace` / `reduced_observability` | trace path reduced | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_capability_confinement` | capability granularity weakened | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_enforcement` | runtime mediation bypassed | `TBD` | `TBD` | `TBD` | `TBD` |

## Notes

- Do not insert synthetic values.
- Keep optional/future baselines as `NA` when not implemented.
- Keep table rows aligned with benchmark matrix slices.
