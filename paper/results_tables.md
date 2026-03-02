# Paper Result Tables

- Source: `bench/results/matrix.json`
- Generated at (UTC): `2026-03-02T23:09:27.651288+00:00`

## Table 1: Baseline Metrics

| Baseline | UER | FAR | TCR | EDS |
|---|---:|---:|---:|---:|
| default | 0.0000 | 0.0000 | 1.0000 | 1.0000 |
| no_plugin_isolation | 0.0000 | 0.0000 | 1.0000 | 1.0000 |
| no_policy | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| no_trace | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| raw_errors | 0.0000 | 1.0000 | 1.0000 | 1.0000 |

## Table 2: Latency

| Baseline | p50 (ms) | p95 (ms) |
|---|---:|---:|
| default | 0.508 | 0.908 |
| no_plugin_isolation | 0.538 | 0.750 |
| no_policy | 0.310 | 0.369 |
| no_trace | 0.104 | 0.211 |
| raw_errors | 0.453 | 0.992 |
