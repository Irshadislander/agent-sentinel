# Pareto Analysis

Safety is defined as `1 - UER_mean`; latency uses `latency_p95_mean`; trace uses `TCR_mean`.

## Points

| baseline | latency_p95_mean | safety (1-UER_mean) | trace (TCR_mean) | pareto |
|---|---:|---:|---:|---:|
| no_trace | 0.192 | 1.0000 | 0.0000 | yes |
| no_policy | 0.432 | 0.0000 | 1.0000 | no |
| default | 0.587 | 1.0000 | 1.0000 | no |
| no_plugin_isolation | 0.603 | 1.0000 | 1.0000 | no |
| raw_errors | 0.611 | 1.0000 | 1.0000 | no |

## Pareto Frontier

- `no_trace`: latency=0.192, safety=1.0000, trace=0.0000
