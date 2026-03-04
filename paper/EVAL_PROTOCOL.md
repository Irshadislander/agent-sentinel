# Evaluation Protocol

## Scenario Set
We evaluate mixed task categories from `configs/tasks/` and matrix outputs from `artifacts/bench/matrix.json`.

Scenario categories:
- `benign`: expected allow.
- `policy_blocked` / `malicious`: expected deny.
- `malformed_payload`: error-path and explainability stress.
- `plugin_failure`: plugin boundary robustness stress.
- `trace_stress`: observability stress.

## Axes
1) **Correctness**: observed decision vs expected decision.
2) **Observability**: trace completeness and presence of `rule_id`/`reason_code`.
3) **Robustness**: attack success and denial-reason distribution.
4) **Performance**: latency p50/p95/p99 and stress scaling.

## Ablations
- `default`: full system (policy + gateway + structured errors + tracing).
- `no_policy`: bypass/disable policy enforcement.
  Expected direction: UER increases, attack success increases.
- `no_trace`: disable trace emission.
  Expected direction: TCR decreases.
- `raw_errors`: replace structured error mapping with raw exception style.
  Expected direction: reason-code coverage and explainability decrease.
- `no_plugin_isolation`: relaxed plugin allowlist isolation.
  Expected direction: plugin-related attack success increases.
- `allowlist_only` / `no_gateway_enforcement` (if enabled in run config): stress unsafe-path behavior.

## Hypotheses by Ablation
- **H1 (Determinism)**: `default` has stable decision/reason outcomes across repeated runs.
- **H2 (Trace Tradeoff)**: `no_trace` lowers TCR while reducing trace overhead.
- **H3 (Safety Enforcement)**: `no_policy` and `no_gateway_enforcement` degrade safety metrics vs `default`.
- **H4 (Explainability)**: `raw_errors` lowers reason-code and rule-id coverage vs structured mode.
- **H5 (Isolation)**: `no_plugin_isolation` increases plugin attack success vs `default`.

## Repetitions
- Matrix runs are repeated across multiple seeds and/or repetitions (minimum 10 when available).
- Aggregation reports mean, delta vs baseline, and bootstrap 95% CI.
- All output tables are generated deterministically from artifact JSON.
