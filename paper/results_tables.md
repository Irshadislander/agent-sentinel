# Paper Result Tables

- Source: `artifacts/bench/matrix.json`
- Generated at (UTC): `2026-03-03T07:45:29.498767+00:00`

## Table 1: Baseline Metrics

| Baseline | UER | ΔUER vs default | FAR | ΔFAR vs default | TCR | ΔTCR vs default | EDS | ΔEDS vs default | plugin_loads | Δplugin_loads vs default |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default | 0.0000 | +0.0000 | 0.0000 | +0.0000 | 1.0000 | +0.0000 | 1.0000 | +0.0000 | 0 | +0 |
| no_plugin_isolation | 0.0000 | +0.0000 | 0.0000 | +0.0000 | 1.0000 | +0.0000 | 1.0000 | +0.0000 | 1 | +1 |
| no_policy | 1.0000 | +1.0000 | 0.0000 | +0.0000 | 1.0000 | +0.0000 | 1.0000 | +0.0000 | 0 | +0 |
| no_trace | 0.0000 | +0.0000 | 0.0000 | +0.0000 | 0.0000 | -1.0000 | 1.0000 | +0.0000 | 0 | +0 |
| raw_errors | 0.0000 | +0.0000 | 1.0000 | +1.0000 | 1.0000 | +0.0000 | 1.0000 | +0.0000 | 0 | +0 |

## Table A: Scale Stability

| scenario_id | N | UER | FAR | TCR | EDS | p50_ms | p95_ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| - | - | - | - | - | - | - | - |

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
| - | - | - | - | - | - | - | - |
