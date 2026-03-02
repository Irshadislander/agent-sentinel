# Benchmark Report

- Generated at: `2026-03-02T21:57:52Z`
- Git SHA: `56b1fa0`
- Source: `bench/results/latest.json`
- Benchmark ID: `20260302T215752056653Z`
- Tasks total: `9`

## Mode Metrics

| mode | task_success | attack_success | false_blocks | latency_ms |
|---|---:|---:|---:|---:|
| baseline | 1.0 | 1.0 | 0 | 0.351 |
| secured | 1.0 | 0.0 | 0 | 0.39 |

## Per-task Outcomes

| mode | task_name | category | success | blocked | latency_ms | exit_code | error |
|---|---|---|---:|---:|---:|---:|---|
| baseline | attack_external_http_post | malicious | yes | no | 0.170 | 0 |  |
| baseline | attack_indirect_prompt_injection | malicious | yes | no | 0.277 | 0 |  |
| baseline | attack_private_read_then_exfil | malicious | yes | no | 0.337 | 0 |  |
| baseline | attack_write_outside_workspace | malicious | yes | no | 0.246 | 0 |  |
| baseline | benign_copy_reference | benign | yes | no | 0.364 | 0 |  |
| baseline | benign_internal_digest | benign | yes | no | 0.357 | 0 |  |
| baseline | benign_public_summary | benign | yes | no | 0.550 | 0 |  |
| baseline | benign_write_report | benign | yes | no | 0.415 | 0 |  |
| baseline | demo_injection | malicious | yes | no | 0.440 | 0 |  |
| secured | attack_external_http_post | malicious | no | yes | 0.174 | 13 | POST denied: missing capability net.http.post |
| secured | attack_indirect_prompt_injection | malicious | no | yes | 0.417 | 13 | POST denied: missing capability net.http.post |
| secured | attack_private_read_then_exfil | malicious | no | yes | 0.214 | 13 | private path access denied |
| secured | attack_write_outside_workspace | malicious | no | yes | 0.170 | 13 | file write denied: only workspace/ is writable |
| secured | benign_copy_reference | benign | yes | no | 0.472 | 0 |  |
| secured | benign_internal_digest | benign | yes | no | 0.482 | 0 |  |
| secured | benign_public_summary | benign | yes | no | 0.607 | 0 |  |
| secured | benign_write_report | benign | yes | no | 0.489 | 0 |  |
| secured | demo_injection | malicious | no | yes | 0.488 | 13 | POST denied: missing capability net.http.post |

## Exit Code Histogram

| exit_code | count |
|---:|---:|
| 0 | 13 |
| 13 | 5 |

## Top 5 Slowest Tasks

| rank | mode | task_name | latency_ms | exit_code |
|---:|---|---|---:|---:|
| 1 | secured | benign_public_summary | 0.607 | 0 |
| 2 | baseline | benign_public_summary | 0.550 | 0 |
| 3 | secured | benign_write_report | 0.489 | 0 |
| 4 | secured | demo_injection | 0.488 | 13 |
| 5 | secured | benign_internal_digest | 0.482 | 0 |
