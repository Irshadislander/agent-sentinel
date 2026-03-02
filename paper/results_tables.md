# Paper Result Tables

- Source: `bench/results/matrix.json`
- Generated at (UTC): `2026-03-02T23:30:24.633234+00:00`

## Table 1: Baseline Metrics

| Baseline | UER | ΔUER vs default | FAR | ΔFAR vs default | TCR | ΔTCR vs default | EDS | ΔEDS vs default | plugin_loads | Δplugin_loads vs default |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default | 0.0000 | +0.0000 | 0.0000 | +0.0000 | 1.0000 | +0.0000 | 1.0000 | +0.0000 | 0 | +0 |
| no_plugin_isolation | 0.0000 | +0.0000 | 0.0000 | +0.0000 | 1.0000 | +0.0000 | 1.0000 | +0.0000 | 1 | +1 |
| no_policy | 1.0000 | +1.0000 | 0.0000 | +0.0000 | 1.0000 | +0.0000 | 1.0000 | +0.0000 | 0 | +0 |
| no_trace | 0.0000 | +0.0000 | 0.0000 | +0.0000 | 0.0000 | -1.0000 | 1.0000 | +0.0000 | 0 | +0 |
| raw_errors | 0.0000 | +0.0000 | 1.0000 | +1.0000 | 1.0000 | +0.0000 | 1.0000 | +0.0000 | 0 | +0 |

## Table 2: Latency

| Baseline | p50 (ms) | p95 (ms) |
|---|---:|---:|
| default | 0.307 | 0.826 |
| no_plugin_isolation | 0.348 | 0.710 |
| no_policy | 0.269 | 0.350 |
| no_trace | 0.108 | 0.363 |
| raw_errors | 0.243 | 0.705 |
