# Statistical Tables

## Reporting Structure

This file is organized into:
1. baseline comparisons,
2. ablation comparisons,
3. attack-family summaries,
4. latency summaries,
5. trace/observability summaries.

Populate templates from measured runs only.

## Baseline Comparisons (Template)

Reference: `default`

| System | ABR mean (95% CI) | ASR mean (95% CI) | ΔABR vs `default` | ΔASR vs `default` | TCR mean (95% CI) | SDAC mean (95% CI) |
|---|---|---|---|---|---|---|
| `default` | `TBD` | `TBD` | `0` | `0` | `TBD` | `TBD` |
| `allow_all` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `naive_allow_list` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_enforcement` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## Ablation Comparisons (Template)

Reference: `full_system`

| Ablation mode | ABR mean (95% CI) | ΔABR vs `full_system` | TCR mean (95% CI) | ΔTCR | SDAC mean (95% CI) | Key interpretation |
|---|---|---|---|---|---|---|
| `full_system` | `TBD` | `0` | `TBD` | `0` | `TBD` | reference |
| `no_default_deny` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_first_match_ordering` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_trace` / `reduced_observability` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_capability_confinement` / `coarse_capability_gating` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_enforcement` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## Attack-Family Summaries (Template)

| Family | Difficulty | System/Ablation | ABR mean (95% CI) | ASR mean (95% CI) | ΔABR vs reference |
|---|---|---|---|---|---|
| `prompt_injection` | `easy` | `TBD` | `TBD` | `TBD` | `TBD` |
| `filesystem_damage` | `medium` | `TBD` | `TBD` | `TBD` | `TBD` |
| `shell_misuse` | `hard` | `TBD` | `TBD` | `TBD` | `TBD` |
| `data_exfiltration` | `medium` | `TBD` | `TBD` | `TBD` | `TBD` |
| `network_exfiltration` | `hard` | `TBD` | `TBD` | `TBD` | `TBD` |

## Latency Summaries

| System/Ablation | p50 (95% CI) | p95 (95% CI) | p99 (95% CI) | Δp95 vs reference |
|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## Trace and Observability Summaries

| System/Ablation | TCR mean (95% CI) | SDAC mean (95% CI) | Reason-code coverage | ΔTCR vs reference |
|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## Existing Populated Outputs
The sections below retain currently generated outputs where available.

## Effect Sizes vs Baseline

Reference baseline: `default`

| Baseline | ΔUER | ΔTCR | ΔLatencyMean(ms) (95% CI) | Cohen's d (latency) |
|---|---:|---:|---|---:|
| default | 0.0000 | 0.0000 | 0.0000 [-0.1496, 0.1487] | 0.0000 |
| no_policy | 0.6667 | 0.0000 | -0.1579 [-0.2747, -0.0503] | -1.0297 |
| no_trace | 0.0000 | -1.0000 | -0.2466 [-0.3606, -0.1443] | -1.6505 |
| raw_errors | 0.0000 | 0.0000 | -0.0143 [-0.1472, 0.1105] | -0.0810 |
| no_plugin_isolation | -0.1111 | 0.0000 | -0.0369 [-0.1678, 0.0852] | -0.2137 |

## Latency Percentile CIs (bootstrap 95%)

| Baseline | p50_ms (95% CI) | p95_ms (95% CI) | p99_ms (95% CI) |
|---|---|---|---|
| default | 0.2269 [0.1772, 0.4374] | 0.6812 [0.4360, 0.8160] | 0.7891 [0.4374, 0.8160] |
| no_policy | 0.2027 [0.1063, 0.2523] | 0.2708 [0.2494, 0.2731] | 0.2727 [0.2523, 0.2731] |
| no_trace | 0.0914 [0.0267, 0.1514] | 0.1770 [0.1397, 0.1913] | 0.1885 [0.1514, 0.1913] |
| raw_errors | 0.2438 [0.1864, 0.4599] | 0.5110 [0.4540, 0.5396] | 0.5339 [0.4599, 0.5396] |
| no_plugin_isolation | 0.2352 [0.1783, 0.4350] | 0.4772 [0.4276, 0.4795] | 0.4791 [0.4350, 0.4795] |

## Policy Engine Perf Cases

| Case | mean_ms | p50_ms | p95_ms | p99_ms |
|---|---:|---:|---:|---:|
| allow_match_early | 0.0016 | 0.0016 | 0.0017 | 0.0021 |
| deny_match_early | 0.0016 | 0.0016 | 0.0017 | 0.0020 |
| invalid_policy | 0.0010 | 0.0010 | 0.0010 | 0.0012 |
| missing_policy | 0.0002 | 0.0002 | 0.0002 | 0.0003 |
| no_match_default_deny | 0.0010 | 0.0010 | 0.0011 | 0.0013 |
