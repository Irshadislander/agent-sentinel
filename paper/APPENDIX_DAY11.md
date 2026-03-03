# Paper Result Tables

- Source: `bench/results/matrix.json`
- Generated at (UTC): `2026-03-02T23:46:11.809720+00:00`

## Table 1: Baseline Metrics

| Baseline | UER | ΔUER vs default | FAR | ΔFAR vs default | TCR | ΔTCR vs default | EDS | ΔEDS vs default | plugin_loads | Δplugin_loads vs default |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default | 0.2468 | +0.0000 | 0.0000 | +0.0000 | 0.8741 | +0.0000 | 0.0900 | +0.0000 | 0 | +0 |
| no_plugin_isolation | 0.2468 | +0.0000 | 0.0000 | +0.0000 | 0.8741 | +0.0000 | 0.0800 | -0.0100 | 1 | +1 |
| no_policy | 0.9810 | +0.7342 | 0.0000 | +0.0000 | 0.8741 | +0.0000 | 0.8450 | +0.7550 | 0 | +0 |
| no_trace | 0.2468 | +0.0000 | 0.0000 | +0.0000 | 0.0000 | -0.8741 | 0.0900 | +0.0000 | 0 | +0 |
| raw_errors | 0.2468 | +0.0000 | 1.0000 | +1.0000 | 0.8741 | +0.0000 | 0.0900 | +0.0000 | 0 | +0 |

## Table A: Scale Stability

| scenario_id | N | UER | FAR | TCR | EDS | p50_ms | p95_ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| scale_n50 | 50 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 0.281 | 0.537 |
| scale_n200 | 200 | 0.2600 | 0.0000 | 0.8662 | 0.0900 | 0.269 | 0.672 |

## Table B: Stress Degradation

| scenario_id | malformed_p | plugin_p | ΔUER | ΔFAR | ΔTCR | ΔEDS | Δp50_ms | Δp95_ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| - | - | - | - | - | - | - | - | - |

## Table C: Sensitivity

| scenario_id | strictness | trace_sample_rate | allowlist_size | UER | FAR | TCR | EDS | p50_ms | p95_ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| - | - | - | - | - | - | - | - | - | - |
