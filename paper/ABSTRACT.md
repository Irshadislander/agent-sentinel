# Abstract

Tool-augmented agents can trigger filesystem, network, and shell-like actions with real side effects, so safety depends on enforcement at runtime tool boundaries rather than prompt quality alone. Existing approaches often emphasize prompt filtering, sandboxing, or orchestration infrastructure in isolation, leaving a gap in deterministic authorization with explainable decisions.

Agent-Sentinel addresses this gap through deterministic runtime capability gating: each request is evaluated against ordered policy rules with default-deny fallback before any tool execution. The key technical contribution is a unified enforcement model with structured decision artifacts (`decision`, `rule_id`, `reason_code`, trace metadata) that supports both formal runtime safety framing and operational auditability.

We evaluate the system under benign and adversarial workloads using baseline and ablation conditions, including targeted control removals (`no_policy`, `no_trace`, `raw_errors`, `no_plugin_isolation`), and report attack blocking, latency overhead, and trace-quality metrics. The artifact pipeline is reproducible from repository workflows and tables.

The practical implication is that secure tool-using agents benefit from deterministic runtime authorization plus machine-auditable decision traces. Scope is intentionally narrow: runtime tool-use enforcement and observability, not general AI safety.

## Links
- [FORMAL_MODEL](FORMAL_MODEL.md)
- [THREAT_MODEL](THREAT_MODEL.md)
- [METRICS](METRICS.md)
- [RESULTS](results_tables.md)
- [ROBUSTNESS](ROBUSTNESS.md)
- [PERF](PERF_DAYXX.md)
