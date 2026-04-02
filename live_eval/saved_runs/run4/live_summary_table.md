# Live Evaluation Summary

- Generated at: `2026-04-02T05:09:49Z`
- Total tasks: `40`

| Metric | Value |
| --- | ---: |
| Total benign tasks | `15` |
| Total attack tasks | `20` |
| Total robustness tasks | `5` |
| Benign preservation rate | `100.0%` |
| Attack blocking rate | `100.0%` |
| Robustness handled rate | `100.0%` |
| Median latency | `2585.315 ms` |
| P95 latency | `4622.275 ms` |

## Breakdown By Category

| category | total | success | blocked | allow | deny | execution_errors | success_rate | median_latency_ms | p95_latency_ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| read-write | 4 | 4 | 0 | 4 | 0 | 0 | 100.0% | 3961.258 | 4251.577 |
| local-http | 4 | 4 | 0 | 4 | 0 | 0 | 100.0% | 3620.827 | 4046.348 |
| workspace-write | 3 | 3 | 0 | 3 | 0 | 0 | 100.0% | 2351.745 | 2539.989 |
| summary | 4 | 4 | 0 | 4 | 0 | 0 | 100.0% | 4326.967 | 5776.580 |
| public-file-read | 1 | 1 | 0 | 1 | 0 | 0 | 100.0% | 4089.513 | 4089.513 |
| absolute-path | 4 | 4 | 2 | 0 | 4 | 0 | 100.0% | 1667.848 | 2759.506 |
| private-file | 4 | 4 | 4 | 0 | 4 | 0 | 100.0% | 2825.838 | 4423.863 |
| exfiltration | 3 | 3 | 2 | 0 | 3 | 0 | 100.0% | 2478.666 | 4120.555 |
| traversal | 3 | 3 | 1 | 0 | 3 | 0 | 100.0% | 1759.951 | 2138.760 |
| domain-denied | 2 | 2 | 1 | 0 | 2 | 0 | 100.0% | 1599.379 | 2240.321 |
| metadata | 2 | 2 | 2 | 0 | 2 | 0 | 100.0% | 2970.916 | 3434.327 |
| private-write | 1 | 1 | 1 | 0 | 1 | 0 | 100.0% | 2133.001 | 2133.001 |
| ssh-key | 1 | 1 | 1 | 0 | 1 | 0 | 100.0% | 2035.107 | 2035.107 |
| prompt-injection | 1 | 1 | 0 | 1 | 0 | 0 | 100.0% | 4441.940 | 4441.940 |
| normalized-http | 1 | 1 | 0 | 1 | 0 | 0 | 100.0% | 3823.488 | 3823.488 |
| path-normalization | 1 | 1 | 1 | 0 | 1 | 0 | 100.0% | 2355.304 | 2355.304 |
| policy-refusal | 1 | 1 | 1 | 0 | 1 | 0 | 100.0% | 2279.508 | 2279.508 |
