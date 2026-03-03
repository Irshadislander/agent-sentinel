# Policy Engine Performance

- Source JSON: `artifacts/bench/policy_engine_bench.json`
- Generated at (UTC): `2026-03-03T07:11:18.049516+00:00`
- Iterations: `1000`
- Warmup: `50`

| case | decision | reason_code | rule_id | mean_ms | p50_ms | p95_ms | p99_ms | trace_len_mean |
|---|---|---|---|---:|---:|---:|---:|---:|
| allow_match_early | allow | RULE_ALLOW_MATCH | allow_early | 0.001346 | 0.001333 | 0.001417 | 0.001459 | 3.00 |
| deny_match_early | deny | RULE_DENY_MATCH | deny_early | 0.001337 | 0.001333 | 0.001416 | 0.001417 | 3.00 |
| invalid_policy | deny | POLICY_INVALID | - | 0.000758 | 0.000750 | 0.000792 | 0.000916 | 2.00 |
| missing_policy | deny | POLICY_MISSING | - | 0.000090 | 0.000083 | 0.000125 | 0.000125 | 2.00 |
| no_match_default_deny | deny | DEFAULT_DENY_NO_MATCH | - | 0.000780 | 0.000791 | 0.000833 | 0.000875 | 3.00 |
