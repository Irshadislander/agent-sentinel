# Paper Result Tables

- Source: `bench/results/matrix.json`
- Generated at (UTC): `2026-03-03T20:46:17.746824+00:00`

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
