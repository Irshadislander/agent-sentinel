# Baseline Comparison

- Source: `artifacts/baselines/baseline_suite.json`
- Generated at (UTC): `2026-03-16T08:56:37.654303+00:00`
- Workload: `/Users/irshadahmad/Documents/agent-sentinel/configs/tasks_synth/scale_n200` (200 scenarios)
- Selection Note: No exact 75-scenario benchmark workload was found. Using the largest pre-generated benchmark workload available (scale_n200): 200 scenarios from /Users/irshadahmad/Documents/agent-sentinel/configs/tasks_synth/scale_n200.
- Security deny categories: `malicious, policy_blocked`
- Robustness categories: `malformed_payload, plugin_failure`

| System | Unsafe Actions Blocked (%) | Safe Actions Allowed (%) | Median Latency (ms) | p95 Latency (ms) | Notes |
|---|---:|---:|---:|---:|---|
| No Protection | 0.00 | 100.00 | 0.02 | 0.10 | Always allow tool execution; no runtime mediation. |
| Static Allowlist | 50.60 | 100.00 | 0.02 | 0.09 | Allow only by tool name; no argument-aware enforcement. |
| Argument Allowlist | 83.13 | 100.00 | 0.06 | 0.24 | Allow by tool name plus simple path and destination checks. |
| Validator Only | 72.29 | 100.00 | 0.05 | 0.14 | Argument validation enabled; capability policy mediation disabled. |
| No Audit | 100.00 | 100.00 | 0.07 | 0.30 | Full mediation path with audit and trace emission disabled. |
| Progent-style | 67.47 | 100.00 | 0.05 | 0.18 | Lightweight rule-based DSL-style policy over tools and arguments. |
| Agent-Sentinel | 100.00 | 100.00 | 0.24 | 0.60 | Full runtime capability mediation with validators and audit trail. |
