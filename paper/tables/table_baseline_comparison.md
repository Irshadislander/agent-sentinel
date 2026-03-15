# Baseline Comparison

- Source: `artifacts/baselines/baseline_suite.json`
- Generated at (UTC): `2026-03-15T06:30:00.729116+00:00`
- Workload: `/Users/irshadahmad/Documents/agent-sentinel/configs/tasks_synth/scale_n200` (200 scenarios)
- Selection Note: No exact 75-scenario benchmark workload was found. Using the largest pre-generated benchmark workload available (scale_n200): 200 scenarios from /Users/irshadahmad/Documents/agent-sentinel/configs/tasks_synth/scale_n200.

| System | Unsafe Actions Blocked (%) | Safe Actions Allowed (%) | Median Latency (ms) | p95 Latency (ms) | Notes |
|---|---:|---:|---:|---:|---|
| No Protection | 0.00 | 100.00 | 0.07 | 0.12 | Always allow tool execution; no runtime mediation. |
| Static Allowlist | 50.59 | 100.00 | 0.07 | 0.10 | Allow only by tool name; no argument-aware enforcement. |
| Argument Allowlist | 50.59 | 100.00 | 0.13 | 0.22 | Allow by tool name plus simple path and destination checks. |
| Validator Only | 50.59 | 100.00 | 0.10 | 0.17 | Argument validation enabled; capability policy mediation disabled. |
| No Audit | 50.59 | 100.00 | 0.14 | 0.23 | Full mediation path with audit and trace emission disabled. |
| Progent-style | 50.59 | 100.00 | 0.15 | 0.25 | Lightweight rule-based DSL-style policy over tools and arguments. |
| Agent-Sentinel | 50.59 | 100.00 | 0.34 | 0.61 | Full runtime capability mediation with validators and audit trail. |
