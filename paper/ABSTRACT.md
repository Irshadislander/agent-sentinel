# Abstract

## Problem
Tool-augmented agents can invoke filesystem, network, and plugin capabilities, but runtime safety behavior is often evaluated qualitatively rather than with deterministic, auditable outcomes.

## Approach
Agent-Sentinel implements deterministic policy resolution at the tool gateway and emits structured decision artifacts (`decision`, `rule_id`, `reason_code`, trace metadata) for each request.

## Evaluation
We evaluate safety, observability, robustness, and latency with controlled ablations (`no_policy`, `no_trace`, `raw_errors`, `no_plugin_isolation`) and adversarial task scenarios.

## Outcome
The framework provides reproducible evidence for tradeoffs between enforcement strength and runtime overhead while preserving stable deny semantics and auditability.

## Links
- [FORMAL_MODEL](FORMAL_MODEL.md)
- [THREAT_MODEL](THREAT_MODEL.md)
- [METRICS](METRICS.md)
- [RESULTS](results_tables.md)
- [ROBUSTNESS](ROBUSTNESS.md)
- [PERF](PERF_DAYXX.md)
