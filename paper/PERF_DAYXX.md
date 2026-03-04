# Policy Engine Performance

- Source JSON: `artifacts/bench/policy_engine_bench.json`
- Generated at (UTC): `2026-03-04T03:45:31.694783+00:00`
- Iterations: `5000`
- Warmup: `200`

| case | decision | reason_code | rule_id | mean_ms | p50_ms | p95_ms | p99_ms | trace_len_mean |
|---|---|---|---|---:|---:|---:|---:|---:|
| allow_match_early | allow | RULE_ALLOW_MATCH | allow_early | 0.001708 | 0.001667 | 0.001833 | 0.002167 | 3.00 |
| deny_match_early | deny | RULE_DENY_MATCH | deny_early | 0.001670 | 0.001666 | 0.002041 | 0.002166 | 3.00 |
| invalid_policy | deny | POLICY_INVALID | - | 0.001036 | 0.001000 | 0.001084 | 0.001292 | 2.00 |
| missing_policy | deny | POLICY_MISSING | - | 0.000196 | 0.000208 | 0.000209 | 0.000250 | 2.00 |
| no_match_default_deny | deny | DEFAULT_DENY_NO_MATCH | - | 0.001030 | 0.001000 | 0.001208 | 0.001333 | 3.00 |

## Stress Scaling Curve (n rules)

| n_rules | p50_ms | p95_ms | p99_ms | trace_len_mean |
|---:|---:|---:|---:|---:|
| 1 | 0.001000 | 0.001333 | 0.001375 | 3.00 |
| 4 | 0.002875 | 0.003000 | 0.003625 | 6.00 |
| 8 | 0.005333 | 0.005875 | 0.006792 | 10.00 |
| 16 | 0.009959 | 0.010875 | 0.012584 | 18.00 |
| 32 | 0.019375 | 0.019921 | 0.023544 | 34.00 |
| 64 | 0.037459 | 0.039919 | 0.044586 | 66.00 |
| 128 | 0.074042 | 0.077048 | 0.086129 | 130.00 |
