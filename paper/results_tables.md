# Paper Result Tables

Use this file for reviewer-facing baseline comparison tables.
Populate from measured artifacts only; do not enter synthetic values.

## Overall Baseline Comparison

Reference: `full_system`

| Baseline | ABR (mean, 95% CI) | ASR (mean, 95% CI) | ΔABR vs `full_system` | ΔASR vs `full_system` | TCR (mean, 95% CI) | SDAC (mean, 95% CI) | Notes |
|---|---|---|---|---|---|---|---|
| `full_system` | `TBD` | `TBD` | `0` | `0` | `TBD` | `TBD` | reference |
| `no_enforcement` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `allow_all` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `naive_allow_list` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `llm_guard_style` (optional/future) | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | mark `NA` if unavailable |

## Baseline Comparison by Attack Family

| Attack family | Baseline | ABR (mean, 95% CI) | ASR (mean, 95% CI) | ΔABR vs `full_system` | ΔASR vs `full_system` | TCR | SDAC |
|---|---|---|---|---|---|---|---|
| `prompt_injection` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `filesystem_damage` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `shell_misuse` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `data_exfiltration` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `network_exfiltration` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## Baseline Comparison by Difficulty

| Difficulty | Baseline | ABR (mean, 95% CI) | ASR (mean, 95% CI) | ΔABR vs `full_system` | ΔASR vs `full_system` | TCR | SDAC |
|---|---|---|---|---|---|---|---|
| `easy` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `medium` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `hard` / `multi_step` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## Overhead Comparison

Reference: `full_system`

| Baseline | p50 latency (mean, 95% CI) | p95 latency (mean, 95% CI) | p99 latency (mean, 95% CI) | Δp50 vs `full_system` | Δp95 vs `full_system` | Δp99 vs `full_system` |
|---|---|---|---|---|---|---|
| `full_system` | `TBD` | `TBD` | `TBD` | `0` | `0` | `0` |
| `no_enforcement` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `allow_all` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `naive_allow_list` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `llm_guard_style` (optional/future) | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` |

## Notes

- Optional/future baseline rows remain in tables but use `NA` when not implemented.
- Use identical workload slices across baselines before computing deltas.
- Keep ablation-specific reporting in [STATS_TABLES](STATS_TABLES.md).
