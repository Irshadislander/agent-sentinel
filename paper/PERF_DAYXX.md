# Policy Engine Performance

- Source JSON: `artifacts/bench/policy_engine_bench.json`
- Generated at (UTC): `2026-03-04T03:31:00.390147+00:00`
- Iterations: `5000`
- Warmup: `200`

| case | decision | reason_code | rule_id | mean_ms | p50_ms | p95_ms | p99_ms | trace_len_mean |
|---|---|---|---|---:|---:|---:|---:|---:|
| allow_match_early | allow | RULE_ALLOW_MATCH | allow_early | 0.001604 | 0.001584 | 0.001709 | 0.002083 | 3.00 |
| deny_match_early | deny | RULE_DENY_MATCH | deny_early | 0.001589 | 0.001625 | 0.001708 | 0.002000 | 3.00 |
| invalid_policy | deny | POLICY_INVALID | - | 0.000983 | 0.001000 | 0.001042 | 0.001250 | 2.00 |
| missing_policy | deny | POLICY_MISSING | - | 0.000199 | 0.000208 | 0.000250 | 0.000250 | 2.00 |
| no_match_default_deny | deny | DEFAULT_DENY_NO_MATCH | - | 0.000989 | 0.000959 | 0.001083 | 0.001291 | 3.00 |

## Stress Scaling Curve (n rules)

| n_rules | p50_ms | p95_ms | p99_ms | trace_len_mean |
|---:|---:|---:|---:|---:|
| 1 | 0.000958 | 0.001333 | 0.001375 | 3.00 |
| 4 | 0.002833 | 0.003000 | 0.003625 | 6.00 |
| 8 | 0.005291 | 0.005417 | 0.005876 | 10.00 |
| 16 | 0.010042 | 0.010375 | 0.011793 | 18.00 |
| 32 | 0.019625 | 0.020000 | 0.024127 | 34.00 |
| 64 | 0.039687 | 0.285273 | 0.679240 | 66.00 |
| 128 | 0.078416 | 0.186735 | 0.456842 | 130.00 |
