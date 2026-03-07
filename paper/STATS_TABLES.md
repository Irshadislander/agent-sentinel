# Statistical Tables

Populate from measured runs only.

## Family-Level Deltas

Reference: family-matched `full_system`

| Attack family | Baseline | Metric | Estimate | 95% CI | Delta | 95% CI of delta |
|---|---|---|---|---|---|---|
| `prompt_injection` | `TBD` | ABR | `TBD` | `TBD` | `TBD` | `TBD` |
| `prompt_injection` | `TBD` | ASR | `TBD` | `TBD` | `TBD` | `TBD` |
| `filesystem_damage` | `TBD` | ABR | `TBD` | `TBD` | `TBD` | `TBD` |
| `filesystem_damage` | `TBD` | ASR | `TBD` | `TBD` | `TBD` | `TBD` |
| `shell_misuse` | `TBD` | ABR | `TBD` | `TBD` | `TBD` | `TBD` |
| `shell_misuse` | `TBD` | ASR | `TBD` | `TBD` | `TBD` | `TBD` |
| `data_exfiltration` | `TBD` | ABR | `TBD` | `TBD` | `TBD` | `TBD` |
| `data_exfiltration` | `TBD` | ASR | `TBD` | `TBD` | `TBD` | `TBD` |
| `network_exfiltration` | `TBD` | ABR | `TBD` | `TBD` | `TBD` | `TBD` |
| `network_exfiltration` | `TBD` | ASR | `TBD` | `TBD` | `TBD` | `TBD` |

## Difficulty-Level Deltas

Reference: difficulty-matched `full_system`

| Difficulty | Baseline | Metric | Estimate | 95% CI | Delta | 95% CI of delta |
|---|---|---|---|---|---|---|
| `easy` | `TBD` | ABR | `TBD` | `TBD` | `TBD` | `TBD` |
| `easy` | `TBD` | ASR | `TBD` | `TBD` | `TBD` | `TBD` |
| `medium` | `TBD` | ABR | `TBD` | `TBD` | `TBD` | `TBD` |
| `medium` | `TBD` | ASR | `TBD` | `TBD` | `TBD` | `TBD` |
| `hard` / `multi_step` | `TBD` | ABR | `TBD` | `TBD` | `TBD` | `TBD` |
| `hard` / `multi_step` | `TBD` | ASR | `TBD` | `TBD` | `TBD` | `TBD` |

## Family-by-Baseline Confidence Intervals

| Attack family | Baseline | ABR (95% CI) | ASR (95% CI) | TCR (95% CI) | SDAC (95% CI) | p95 latency (95% CI) |
|---|---|---|---|---|---|---|
| `prompt_injection` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `filesystem_damage` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `shell_misuse` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `data_exfiltration` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `network_exfiltration` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## Notes

- Use identical workload slices across baselines before delta computation.
- Declare a single CI method and apply it consistently.
- Report optional/future baselines as `NA` when unavailable.
