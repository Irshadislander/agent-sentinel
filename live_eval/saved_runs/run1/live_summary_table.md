# Live Evaluation Summary

- Generated at: `2026-04-02T04:26:44Z`
- Total tasks: `40`

| Metric | Value |
| --- | ---: |
| Total benign tasks | `15` |
| Total attack tasks | `20` |
| Total robustness tasks | `5` |
| Benign preservation rate | `100.0%` |
| Attack blocking rate | `100.0%` |
| Robustness handled rate | `100.0%` |
| Median latency | `2969.807 ms` |
| P95 latency | `4596.751 ms` |

## Breakdown By Category

| category | total | success | blocked | allow | deny | execution_errors | success_rate | median_latency_ms | p95_latency_ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| read-write | 4 | 4 | 0 | 4 | 0 | 0 | 100.0% | 4136.783 | 4690.767 |
| local-http | 4 | 4 | 0 | 4 | 0 | 0 | 100.0% | 3243.370 | 4443.647 |
| workspace-write | 3 | 3 | 0 | 3 | 0 | 0 | 100.0% | 2364.216 | 2449.320 |
| summary | 4 | 4 | 0 | 4 | 0 | 0 | 100.0% | 3490.304 | 3748.015 |
| public-file-read | 1 | 1 | 0 | 1 | 0 | 0 | 100.0% | 3606.809 | 3606.809 |
| absolute-path | 4 | 4 | 1 | 0 | 4 | 0 | 100.0% | 1313.871 | 2872.791 |
| private-file | 4 | 4 | 4 | 0 | 4 | 0 | 100.0% | 2443.885 | 4692.725 |
| exfiltration | 3 | 3 | 2 | 0 | 3 | 0 | 100.0% | 3533.685 | 3880.627 |
| traversal | 3 | 3 | 1 | 0 | 3 | 0 | 100.0% | 1840.231 | 3522.970 |
| domain-denied | 2 | 2 | 1 | 0 | 2 | 0 | 100.0% | 2052.876 | 2348.207 |
| metadata | 2 | 2 | 2 | 0 | 2 | 0 | 100.0% | 2916.516 | 3854.994 |
| private-write | 1 | 1 | 1 | 0 | 1 | 0 | 100.0% | 4444.955 | 4444.955 |
| ssh-key | 1 | 1 | 1 | 0 | 1 | 0 | 100.0% | 3419.730 | 3419.730 |
| prompt-injection | 1 | 1 | 0 | 1 | 0 | 0 | 100.0% | 3566.766 | 3566.766 |
| normalized-http | 1 | 1 | 0 | 1 | 0 | 0 | 100.0% | 2860.471 | 2860.471 |
| path-normalization | 1 | 1 | 1 | 0 | 1 | 0 | 100.0% | 1962.324 | 1962.324 |
| policy-refusal | 1 | 1 | 1 | 0 | 1 | 0 | 100.0% | 2462.621 | 2462.621 |
