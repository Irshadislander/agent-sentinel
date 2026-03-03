# Policy Engine Performance

- Source JSON: `artifacts/bench/policy_engine_bench.json`
- Generated at (UTC): `2026-03-03T07:43:48.998574+00:00`
- Iterations: `5000`
- Warmup: `200`

| case | decision | reason_code | rule_id | mean_ms | p50_ms | p95_ms | p99_ms | trace_len_mean |
|---|---|---|---|---:|---:|---:|---:|---:|
| allow_match_early | allow | RULE_ALLOW_MATCH | allow_early | 0.001204 | 0.001208 | 0.001292 | 0.001583 | 3.00 |
| deny_match_early | deny | RULE_DENY_MATCH | deny_early | 0.001193 | 0.001167 | 0.001292 | 0.001583 | 3.00 |
| invalid_policy | deny | POLICY_INVALID | - | 0.000681 | 0.000667 | 0.000750 | 0.000833 | 2.00 |
| missing_policy | deny | POLICY_MISSING | - | 0.000087 | 0.000083 | 0.000125 | 0.000125 | 2.00 |
| no_match_default_deny | deny | DEFAULT_DENY_NO_MATCH | - | 0.000735 | 0.000750 | 0.000792 | 0.000958 | 3.00 |

## Stress Scaling Curve (n rules)

| n_rules | p50_ms | p95_ms | p99_ms | trace_len_mean |
|---:|---:|---:|---:|---:|
| 1 | 0.000750 | 0.001041 | 0.001083 | 3.00 |
| 4 | 0.002188 | 0.002458 | 0.002500 | 6.00 |
| 8 | 0.003792 | 0.004542 | 0.005460 | 10.00 |
| 16 | 0.007875 | 0.008961 | 0.010710 | 18.00 |
| 32 | 0.015583 | 0.016834 | 0.019667 | 34.00 |
| 64 | 0.030584 | 0.033419 | 0.038126 | 66.00 |
| 128 | 0.061458 | 0.063777 | 0.074130 | 130.00 |
