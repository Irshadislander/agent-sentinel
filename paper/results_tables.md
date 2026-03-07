# Paper Result Tables

Populate all cells from measured artifacts only.

## Overall Baseline Comparison

Reference: `full_system`

| Baseline | ABR (mean, 95% CI) | ASR (mean, 95% CI) | ΔABR vs `full_system` | ΔASR vs `full_system` | TCR (mean, 95% CI) | SDAC (mean, 95% CI) | Notes |
|---|---|---|---|---|---|---|---|
| `full_system` | `TBD` | `TBD` | `0` | `0` | `TBD` | `TBD` | reference |
| `no_enforcement` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `allow_all` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `naive_allow_list` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `llm_guard_style` (optional/future) | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | `TBD/NA` | use `NA` if unavailable |

## Attack Family Summary

| Attack family | ABR (mean, 95% CI) | ASR (mean, 95% CI) | TCR (mean, 95% CI) | SDAC (mean, 95% CI) | Interpretation |
|---|---|---|---|---|---|
| `prompt_injection` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `filesystem_damage` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `shell_misuse` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `data_exfiltration` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `network_exfiltration` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## Difficulty-Level Summary

| Difficulty | ABR (mean, 95% CI) | ASR (mean, 95% CI) | TCR (mean, 95% CI) | SDAC (mean, 95% CI) | Interpretation |
|---|---|---|---|---|---|
| `easy` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `medium` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `hard` / `multi_step` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## Family × Difficulty Comparison

| Attack family | Difficulty | Baseline | ABR (mean, 95% CI) | ASR (mean, 95% CI) | ΔABR vs family-level `full_system` | ΔASR vs family-level `full_system` |
|---|---|---|---|---|---|---|
| `prompt_injection` | `easy` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `prompt_injection` | `medium` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `prompt_injection` | `hard` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `filesystem_damage` | `easy` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `filesystem_damage` | `medium` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `filesystem_damage` | `hard` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `shell_misuse` | `easy` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `shell_misuse` | `medium` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `shell_misuse` | `hard` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `data_exfiltration` | `easy` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `data_exfiltration` | `medium` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `data_exfiltration` | `hard` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `network_exfiltration` | `easy` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `network_exfiltration` | `medium` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `network_exfiltration` | `hard` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## Per-Family Baseline Comparison

| Attack family | Baseline | ABR (mean, 95% CI) | ASR (mean, 95% CI) | TCR (mean, 95% CI) | SDAC (mean, 95% CI) | ΔABR vs family `full_system` | ΔASR vs family `full_system` |
|---|---|---|---|---|---|---|---|
| `prompt_injection` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `filesystem_damage` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `shell_misuse` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `data_exfiltration` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `network_exfiltration` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## Notes

- Keep optional/future baseline rows and report `NA` if unavailable.
- Do not insert synthetic or estimated values.
- Use identical workload slices for valid delta computation.
