# Paper Result Tables

- Source: `bench/results/day12_aggregate.json`
- Generated at (UTC): `2026-03-02T23:58:18.665912+00:00`

## Table X: Stability Across Seeds (mean ± std)

| baseline | scenario_id | UER (mean±std) | FAR (mean±std) | TCR (mean±std) | EDS (mean±std) | plugin_loads (mean±std) | p95 latency ms (mean±std) |
|---|---|---|---|---|---|---|---|
| default | scale_n200 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 0.00 ± 0.00 | 0.587 ± 0.115 |
| no_plugin_isolation | scale_n200 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.00 ± 0.00 | 0.603 ± 0.082 |
| no_policy | scale_n200 | 1.0000 ± 0.0000 | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 0.00 ± 0.00 | 0.432 ± 0.147 |
| no_trace | scale_n200 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | 0.00 ± 0.00 | 0.192 ± 0.035 |
| raw_errors | scale_n200 | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 0.00 ± 0.00 | 0.611 ± 0.066 |
