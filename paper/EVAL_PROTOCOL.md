# Evaluation Protocol

## Axes
1) Correctness: decision matches expected outcome for each test case.
2) Observability: trace completeness and presence of rule_id/reason_code.
3) Robustness: attack scenario success rate and trace integrity under attack.
4) Performance: latency p50/p95/p99 under stress settings.

## Ablations (causal)
- A0: full system (baseline)
- A1: no_policy (missing policy) → expect deny + validation reason code
- A2: raw_errors (no structured reason codes) → expect lower explainability score
- A3: no_trace (trace suppressed) → expect trace completeness drop
- A4: allowlist_only → expect higher attack success for escalation attempts
- A5: no_gateway_enforcement (simulated) → expect safety collapse (if modeled)

## Hypotheses
- H1: Deterministic engine yields 100% determinism and stable reason codes.
- H2: Trace-enabled configuration increases auditability with bounded overhead.
- H3: Gateway enforcement prevents tool escalation in attack scenarios.
- H4: Stress axis shows bounded p95/p99 latency under typical policy sizes.
