# Policy Engine Performance

- Source JSON: `artifacts/bench/policy_engine_bench.json`
- Generated at (UTC): `2026-03-03T20:46:17.482820+00:00`
- Iterations: `5000`
- Warmup: `200`

| case | decision | reason_code | rule_id | mean_ms | p50_ms | p95_ms | p99_ms | trace_len_mean |
|---|---|---|---|---:|---:|---:|---:|---:|
| allow_match_early | allow | RULE_ALLOW_MATCH | allow_early | 0.001671 | 0.001625 | 0.002000 | 0.002125 | 3.00 |
| deny_match_early | deny | RULE_DENY_MATCH | deny_early | 0.001695 | 0.001667 | 0.002083 | 0.002125 | 3.00 |
| invalid_policy | deny | POLICY_INVALID | - | 0.002725 | 0.000959 | 0.002250 | 0.003626 | 2.00 |
| missing_policy | deny | POLICY_MISSING | - | 0.000550 | 0.000375 | 0.000417 | 0.001167 | 2.00 |
| no_match_default_deny | deny | DEFAULT_DENY_NO_MATCH | - | 0.001034 | 0.001000 | 0.001250 | 0.001333 | 3.00 |

## Stress Scaling Curve (n rules)

| n_rules | p50_ms | p95_ms | p99_ms | trace_len_mean |
|---:|---:|---:|---:|---:|
| 1 | 0.001083 | 0.001416 | 0.024598 | 3.00 |
| 4 | 0.003042 | 0.010601 | 0.043853 | 6.00 |
| 8 | 0.005333 | 0.005583 | 0.005875 | 10.00 |
| 16 | 0.010167 | 0.010500 | 0.012292 | 18.00 |
| 32 | 0.019750 | 0.022794 | 0.024543 | 34.00 |
| 64 | 0.038208 | 0.039586 | 0.044291 | 66.00 |
| 128 | 0.076666 | 0.083545 | 0.105699 | 130.00 |
