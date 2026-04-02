# Live Evaluation Summary

- Generated at: `2026-04-02T05:11:55Z`
- Total tasks: `40`

| Metric | Value |
| --- | ---: |
| Total benign tasks | `15` |
| Total attack tasks | `20` |
| Total robustness tasks | `5` |
| Benign preservation rate | `100.0%` |
| Attack blocking rate | `100.0%` |
| Robustness handled rate | `100.0%` |
| Median latency | `2457.765 ms` |
| P95 latency | `4457.621 ms` |

## Breakdown By Category

| category | total | success | blocked | allow | deny | execution_errors | success_rate | median_latency_ms | p95_latency_ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| read-write | 4 | 4 | 0 | 4 | 0 | 0 | 100.0% | 4118.914 | 4798.967 |
| local-http | 4 | 4 | 0 | 4 | 0 | 0 | 100.0% | 3493.099 | 4138.883 |
| workspace-write | 3 | 3 | 0 | 3 | 0 | 0 | 100.0% | 2105.862 | 2775.327 |
| summary | 4 | 4 | 0 | 4 | 0 | 0 | 100.0% | 4118.155 | 4891.414 |
| public-file-read | 1 | 1 | 0 | 1 | 0 | 0 | 100.0% | 4435.466 | 4435.466 |
| absolute-path | 4 | 4 | 1 | 0 | 4 | 0 | 100.0% | 995.194 | 2250.405 |
| private-file | 4 | 4 | 4 | 0 | 4 | 0 | 100.0% | 2489.109 | 3876.975 |
| exfiltration | 3 | 3 | 2 | 0 | 3 | 0 | 100.0% | 2252.657 | 3511.177 |
| traversal | 3 | 3 | 1 | 0 | 3 | 0 | 100.0% | 1083.747 | 2116.121 |
| domain-denied | 2 | 2 | 1 | 0 | 2 | 0 | 100.0% | 1561.374 | 2321.857 |
| metadata | 2 | 2 | 2 | 0 | 2 | 0 | 100.0% | 2348.651 | 2446.243 |
| private-write | 1 | 1 | 1 | 0 | 1 | 0 | 100.0% | 2368.367 | 2368.367 |
| ssh-key | 1 | 1 | 1 | 0 | 1 | 0 | 100.0% | 2972.240 | 2972.240 |
| prompt-injection | 1 | 1 | 0 | 1 | 0 | 0 | 100.0% | 3808.760 | 3808.760 |
| normalized-http | 1 | 1 | 0 | 1 | 0 | 0 | 100.0% | 3116.040 | 3116.040 |
| path-normalization | 1 | 1 | 1 | 0 | 1 | 0 | 100.0% | 1989.831 | 1989.831 |
| policy-refusal | 1 | 1 | 1 | 0 | 1 | 0 | 100.0% | 2190.331 | 2190.331 |
