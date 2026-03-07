# Statistical Tables (Final Freeze)

All values should be computed from benchmark outputs (`matrix.json` / `matrix.csv` style aggregates). Populate from measured runs only.

## 1. Confidence Interval Reporting

| Metric | Estimate | 95% CI | Reference | Delta vs reference | 95% CI of delta |
|---|---|---|---|---|---|
| ABR | `TBD` | `TBD` | `full_system` | `TBD` | `TBD` |
| ASR | `TBD` | `TBD` | `full_system` | `TBD` | `TBD` |
| p50 latency | `TBD` | `TBD` | `full_system` | `TBD` | `TBD` |
| p95 latency | `TBD` | `TBD` | `full_system` | `TBD` | `TBD` |
| throughput | `TBD` | `TBD` | `full_system` | `TBD` | `TBD` |
| TCR | `TBD` | `TBD` | `full_system` | `TBD` | `TBD` |
| SDAC | `TBD` | `TBD` | `full_system` | `TBD` | `TBD` |

## 2. Baseline Deltas

| Baseline | ΔABR | ΔASR | Δp95 latency | Δthroughput | ΔTCR | ΔSDAC |
|---|---|---|---|---|---|---|
| `no_enforcement` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `allow_all` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `naive_allow_list` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `llm_guard_style` (optional/future) | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` |

## 3. Family-Level Deltas

| Attack family | Baseline | ΔABR | ΔASR | ΔTCR | ΔSDAC | Δp95 latency |
|---|---|---|---|---|---|---|
| `prompt_injection` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `filesystem_damage` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `shell_misuse` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `data_exfiltration` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `network_exfiltration` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## 4. Difficulty-Level Deltas

| Difficulty | Baseline | ΔABR | ΔASR | ΔTCR | ΔSDAC | Δp95 latency |
|---|---|---|---|---|---|---|
| `easy` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `medium` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `hard` / `multi_step` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## 5. Performance Summaries

| Baseline | p50 (mean, 95% CI) | p95 (mean, 95% CI) | p99 (mean, 95% CI) | Throughput (mean, 95% CI) | Scale ratio summary |
|---|---|---|---|---|---|
| `full_system` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_enforcement` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `allow_all` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `naive_allow_list` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `llm_guard_style` (optional/future) | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` |

## Notes

- Declare one CI method and apply it consistently.
- Keep slices aligned with matrix axes (family, difficulty, baseline).
- Report optional/future baselines as `NA` when unavailable.
