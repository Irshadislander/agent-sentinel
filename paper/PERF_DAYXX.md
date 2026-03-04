# Policy Engine Performance

- Source JSON: `artifacts/bench/policy_engine_bench.json`
- Generated at (UTC): `2026-03-04T03:03:13.309367+00:00`
- Iterations: `5000`
- Warmup: `200`

| case | decision | reason_code | rule_id | mean_ms | p50_ms | p95_ms | p99_ms | trace_len_mean |
|---|---|---|---|---:|---:|---:|---:|---:|
| allow_match_early | allow | RULE_ALLOW_MATCH | allow_early | 0.001540 | 0.001500 | 0.001667 | 0.001792 | 3.00 |
| deny_match_early | deny | RULE_DENY_MATCH | deny_early | 0.001521 | 0.001500 | 0.001666 | 0.002042 | 3.00 |
| invalid_policy | deny | POLICY_INVALID | - | 0.000929 | 0.000917 | 0.001041 | 0.001125 | 2.00 |
| missing_policy | deny | POLICY_MISSING | - | 0.000190 | 0.000208 | 0.000209 | 0.000250 | 2.00 |
| no_match_default_deny | deny | DEFAULT_DENY_NO_MATCH | - | 0.001003 | 0.001000 | 0.001084 | 0.001292 | 3.00 |

## Stress Scaling Curve (n rules)

| n_rules | p50_ms | p95_ms | p99_ms | trace_len_mean |
|---:|---:|---:|---:|---:|
| 1 | 0.000958 | 0.001250 | 0.001375 | 3.00 |
| 4 | 0.002542 | 0.002833 | 0.003208 | 6.00 |
| 8 | 0.004708 | 0.005209 | 0.005423 | 10.00 |
| 16 | 0.009542 | 0.009791 | 0.011709 | 18.00 |
| 32 | 0.018541 | 0.019044 | 0.023169 | 34.00 |
| 64 | 0.034334 | 0.038044 | 0.042985 | 66.00 |
| 128 | 0.072875 | 0.076500 | 0.081210 | 130.00 |
