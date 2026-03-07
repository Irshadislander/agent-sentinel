# Paper Result Tables

- Source: `bench/results/matrix.json`
- Generated at (UTC): `2026-03-04T03:45:31.936492+00:00`

## Reporting Map

This file is structured so reviewers can quickly identify:
1. systems compared,
2. primary metrics,
3. baseline comparison outputs,
4. ablation comparison outputs.

## Systems Compared (Template)

| System label | Type | Implemented in this run? | Notes |
|---|---|---|---|
| `default` / `full_system` | reference | yes/no | runtime enforcement + structured decision artifacts |
| `allow_all` | baseline condition | yes/no | permissive policy condition |
| `naive_allow_list` | baseline condition | yes/no | simplified capability allow-list |
| `no_enforcement` | baseline/ablation condition | yes/no | enforcement bypass |
| `no_default_deny` | ablation mode | yes/no | default-deny weakened |
| `no_first_match_ordering` | ablation mode | yes/no | deterministic ordering weakened |
| `no_trace` / `reduced_observability` | ablation mode | yes/no | trace coverage reduced |
| `no_capability_confinement` / `coarse_capability_gating` | ablation mode | yes/no | capability boundary weakened |

## Primary Metrics (Template)

| System/Ablation | ABR | ASR | Latency overhead (p50/p95/p99) | TCR | SDAC | Source section |
|---|---|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | baseline/ablation table id |

## Ablation Summary (Template)

Populate this section from measured runs only (no synthetic values).

| Ablation mode | Component changed | Expected primary failure mode | Implemented in current run? | Observed summary |
|---|---|---|---|---|
| `full_system` | none | reference behavior | yes/no | `TBD` |
| `no_default_deny` | default-deny fallback removed/weakened | unmatched unsafe requests can pass | yes/no | `TBD` |
| `no_first_match_ordering` | deterministic ordering removed | conflicting-rule instability | yes/no | `TBD` |
| `no_trace` / `reduced_observability` | tracing reduced/disabled | audit/observability degradation | yes/no | `TBD` |
| `no_capability_confinement` / `coarse_capability_gating` | capability boundary weakened | privilege overreach | yes/no | `TBD` |
| `no_enforcement` | enforcement bypassed | largest attack success increase | yes/no | `TBD` |

## Expected Effect on Block Rate (Template)

| Ablation mode | Expected direction vs `full_system` | Observed ABR | ΔABR |
|---|---|---|---|
| `no_default_deny` | decrease | `TBD` | `TBD` |
| `no_first_match_ordering` | decrease / unstable by family | `TBD` | `TBD` |
| `no_trace` / `reduced_observability` | near-neutral to slight decrease | `TBD` | `TBD` |
| `no_capability_confinement` / `coarse_capability_gating` | decrease | `TBD` | `TBD` |
| `no_enforcement` | largest decrease | `TBD` | `TBD` |

## Expected Effect on Latency (Template)

| Ablation mode | Expected direction vs `full_system` | Observed p50/p95 overhead |
|---|---|---|
| `no_default_deny` | mixed (path dependent) | `TBD` |
| `no_first_match_ordering` | mixed / implementation dependent | `TBD` |
| `no_trace` / `reduced_observability` | decrease expected | `TBD` |
| `no_capability_confinement` / `coarse_capability_gating` | slight decrease expected | `TBD` |
| `no_enforcement` | decrease expected | `TBD` |

## Expected Effect on Trace Completeness (Template)

| Ablation mode | Expected direction vs `full_system` | Observed TCR | ΔTCR |
|---|---|---|---|
| `no_default_deny` | neutral to slight decrease | `TBD` | `TBD` |
| `no_first_match_ordering` | neutral to slight decrease | `TBD` | `TBD` |
| `no_trace` / `reduced_observability` | largest decrease | `TBD` | `TBD` |
| `no_capability_confinement` / `coarse_capability_gating` | slight decrease | `TBD` | `TBD` |
| `no_enforcement` | moderate decrease / path dependent | `TBD` | `TBD` |

## Baseline Results
Primary baseline comparison tables appear here first.

## Table 1: Baseline Metrics

| Baseline | UER | ΔUER vs default | FAR | ΔFAR vs default | TCR | ΔTCR vs default | EDS | ΔEDS vs default | plugin_loads | Δplugin_loads vs default |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default | 0.2468 | +0.0000 | 0.0000 | +0.0000 | 0.8741 | +0.0000 | 0.0900 | +0.0000 | 0 | +0 |
| no_plugin_isolation | 0.2468 | +0.0000 | 0.0000 | +0.0000 | 0.8741 | +0.0000 | 0.0800 | -0.0100 | 1 | +1 |
| no_policy | 0.9810 | +0.7342 | 0.0000 | +0.0000 | 0.8741 | +0.0000 | 0.8450 | +0.7550 | 0 | +0 |
| no_trace | 0.2468 | +0.0000 | 0.0000 | +0.0000 | 0.0000 | -0.8741 | 0.0900 | +0.0000 | 0 | +0 |
| raw_errors | 0.2468 | +0.0000 | 1.0000 | +1.0000 | 0.8741 | +0.0000 | 0.0900 | +0.0000 | 0 | +0 |

## Ablation Results
Use the ablation templates above for implemented ablation modes.
Keep unimplemented modes explicitly as placeholders.

## Table A: Scale Stability

| scenario_id | N | UER | FAR | TCR | EDS | p50_ms | p95_ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| scale_n50 | 50 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 0.265 | 0.850 |
| scale_n200 | 200 | 0.2600 | 0.0000 | 0.8662 | 0.0900 | 0.242 | 0.543 |

## Table B: Stress Degradation

| scenario_id | malformed_p | plugin_p | ΔUER | ΔFAR | ΔTCR | ΔEDS | Δp50_ms | Δp95_ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| - | - | - | - | - | - | - | - | - |

## Table C: Sensitivity

| scenario_id | strictness | trace_sample_rate | allowlist_size | UER | FAR | TCR | EDS | p50_ms | p95_ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| - | - | - | - | - | - | - | - | - | - |

## Table X: Stability Across Seeds (mean ± std)

| baseline | scenario_id | UER (mean±std) | FAR (mean±std) | TCR (mean±std) | EDS (mean±std) | plugin_loads (mean±std) | p95 latency ms (mean±std) |
|---|---|---|---|---|---|---|---|
| default | scale_n200 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 0.00 ± 0.00 | 0.587 ± 0.115 |
| no_plugin_isolation | scale_n200 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.00 ± 0.00 | 0.603 ± 0.082 |
| no_policy | scale_n200 | 1.0000 ± 0.0000 | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 0.00 ± 0.00 | 0.432 ± 0.147 |
| no_trace | scale_n200 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | 0.00 ± 0.00 | 0.192 ± 0.035 |
| raw_errors | scale_n200 | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 0.00 ± 0.00 | 0.611 ± 0.066 |
