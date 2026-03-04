# Abstract

## What
We study runtime capability gating for tool-augmented agents as a deterministic systems problem.

## Why
Safety mechanisms for tool use are commonly evaluated qualitatively, making it difficult to isolate causal effects of policy enforcement, tracing, and isolation controls.

## How
Agent-Sentinel enforces deterministic rule resolution at runtime and emits structured decision artifacts (`decision`, `rule_id`, `reason_code`, trace metadata). We evaluate controlled ablations (`no_policy`, `no_trace`, `raw_errors`, `no_plugin_isolation`) under benign and adversarial workloads.

## Results
The evaluation quantifies safety-observability-extensibility tradeoffs and shows measurable degradation when key controls are removed, while preserving stable deny semantics in full mode.

## Artifacts
We provide formal specifications, adversarial protocols, benchmark matrix outputs, and canonical report-generation scripts for reproducible analysis.

## Links
- [FORMAL_MODEL](FORMAL_MODEL.md)
- [THREAT_MODEL](THREAT_MODEL.md)
- [METRICS](METRICS.md)
- [RESULTS](results_tables.md)
- [ROBUSTNESS](ROBUSTNESS.md)
- [PERF](PERF_DAYXX.md)
