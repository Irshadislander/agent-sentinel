# Paper Result Tables

- Source: `bench/results/matrix.json`
- Generated at (UTC): `2026-03-02T23:17:57.250923+00:00`

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
| default | 0.239 | 0.554 |
| no_plugin_isolation | 0.270 | 0.762 |
| no_policy | 0.204 | 0.276 |
| no_trace | 0.084 | 0.173 |
| raw_errors | 0.394 | 1.651 |
