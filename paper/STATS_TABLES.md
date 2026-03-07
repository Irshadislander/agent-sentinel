# Statistical Tables

## Ablation Statistical Reporting (Template)

Populate these tables from measured ablation runs only.

### Ablation Summary

| Ablation mode | Hypothesis | Expected degradation axis | Statistical output placeholder |
|---|---|---|---|
| `no_default_deny` | removing deny fallback increases unsafe allows | safety / block rate | `TBD` |
| `no_first_match_ordering` | removing deterministic ordering increases instability | safety consistency / explainability | `TBD` |
| `no_trace` / `reduced_observability` | reducing trace lowers observability | trace completeness / artifact coverage | `TBD` |
| `no_capability_confinement` / `coarse_capability_gating` | weakening capability boundary increases unsafe execution | safety / block rate | `TBD` |
| `no_enforcement` | bypassing enforcement maximizes attack success | safety | `TBD` |

### Expected Effect on Block Rate (Template)

| Ablation mode | ABR mean (`full_system`) | ABR mean (ablation) | ΔABR | CI / significance |
|---|---|---|---|---|
| `no_default_deny` | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_first_match_ordering` | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_trace` / `reduced_observability` | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_capability_confinement` / `coarse_capability_gating` | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_enforcement` | `TBD` | `TBD` | `TBD` | `TBD` |

### Expected Effect on Latency (Template)

| Ablation mode | Δp50 vs `full_system` | Δp95 vs `full_system` | CI / effect size |
|---|---|---|---|
| `no_default_deny` | `TBD` | `TBD` | `TBD` |
| `no_first_match_ordering` | `TBD` | `TBD` | `TBD` |
| `no_trace` / `reduced_observability` | `TBD` | `TBD` | `TBD` |
| `no_capability_confinement` / `coarse_capability_gating` | `TBD` | `TBD` | `TBD` |
| `no_enforcement` | `TBD` | `TBD` | `TBD` |

### Expected Effect on Trace Completeness (Template)

| Ablation mode | TCR mean (`full_system`) | TCR mean (ablation) | ΔTCR | CI / significance |
|---|---|---|---|---|
| `no_default_deny` | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_first_match_ordering` | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_trace` / `reduced_observability` | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_capability_confinement` / `coarse_capability_gating` | `TBD` | `TBD` | `TBD` | `TBD` |
| `no_enforcement` | `TBD` | `TBD` | `TBD` | `TBD` |

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
