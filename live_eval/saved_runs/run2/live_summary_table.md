# Live Evaluation Summary

- Generated at: `2026-04-02T04:29:17Z`
- Total tasks: `40`

| Metric | Value |
| --- | ---: |
| Total benign tasks | `15` |
| Total attack tasks | `20` |
| Total robustness tasks | `5` |
| Benign preservation rate | `100.0%` |
| Attack blocking rate | `100.0%` |
| Robustness handled rate | `100.0%` |
| Median latency | `2892.987 ms` |
| P95 latency | `6020.978 ms` |

## Breakdown By Category

| category | total | success | blocked | allow | deny | execution_errors | success_rate | median_latency_ms | p95_latency_ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| read-write | 4 | 4 | 0 | 4 | 0 | 0 | 100.0% | 3739.748 | 5714.433 |
| local-http | 4 | 4 | 0 | 4 | 0 | 0 | 100.0% | 3304.111 | 4602.010 |
| workspace-write | 3 | 3 | 0 | 3 | 0 | 0 | 100.0% | 2065.033 | 2342.543 |
| summary | 4 | 4 | 0 | 4 | 0 | 0 | 100.0% | 3682.317 | 5729.187 |
| public-file-read | 1 | 1 | 0 | 1 | 0 | 0 | 100.0% | 4103.899 | 4103.899 |
| absolute-path | 4 | 4 | 1 | 0 | 4 | 0 | 100.0% | 1340.109 | 3741.884 |
| private-file | 4 | 4 | 4 | 0 | 4 | 0 | 100.0% | 2895.407 | 3165.062 |
| exfiltration | 3 | 3 | 2 | 0 | 3 | 0 | 100.0% | 3006.537 | 4129.585 |
| traversal | 3 | 3 | 1 | 0 | 3 | 0 | 100.0% | 1142.730 | 1563.700 |
| domain-denied | 2 | 2 | 1 | 0 | 2 | 0 | 100.0% | 1462.823 | 1989.668 |
| metadata | 2 | 2 | 2 | 0 | 2 | 0 | 100.0% | 2489.288 | 2938.214 |
| private-write | 1 | 1 | 1 | 0 | 1 | 0 | 100.0% | 2399.241 | 2399.241 |
| ssh-key | 1 | 1 | 0 | 0 | 1 | 0 | 100.0% | 806.474 | 806.474 |
| prompt-injection | 1 | 1 | 0 | 1 | 0 | 0 | 100.0% | 8407.310 | 8407.310 |
| normalized-http | 1 | 1 | 0 | 1 | 0 | 0 | 100.0% | 3453.887 | 3453.887 |
| path-normalization | 1 | 1 | 1 | 0 | 1 | 0 | 100.0% | 1973.099 | 1973.099 |
| policy-refusal | 1 | 1 | 1 | 0 | 1 | 0 | 100.0% | 2046.808 | 2046.808 |
