# Method

## System Pipeline
Requests pass through a single gateway that resolves capability decisions before any tool invocation. The resolver returns structured outputs including verdict, rule match, and reason code.

## Enforcement Semantics
Policy rules are evaluated deterministically with explicit precedence and default deny fallback. Invalid or missing policies map to stable deny reason codes.

## Observability
Each request emits a structured audit event with decision metadata and trace summary fields used for completeness and integrity checks.

## Ablation Design
Controlled toggles remove one safeguard at a time (`no_policy`, `no_trace`, `raw_errors`, `no_plugin_isolation`) to isolate causal effects on safety and runtime behavior.

## Links
- [FORMAL_MODEL](FORMAL_MODEL.md)
- [THREAT_MODEL](THREAT_MODEL.md)
- [METRICS](METRICS.md)
- [RESULTS](results_tables.md)
- [ROBUSTNESS](ROBUSTNESS.md)
- [PERF](PERF_DAYXX.md)
