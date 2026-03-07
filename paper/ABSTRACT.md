# Abstract

Tool-using AI agents can trigger filesystem, network, and shell side effects, so security depends on runtime control at the tool boundary, not only on prompt quality. Existing approaches often emphasize prompt guardrails, orchestration, or isolation in isolation, leaving a gap in deterministic request-level authorization with formalized behavior.

Agent-Sentinel addresses this gap with capability-based runtime enforcement: each tool request is mediated by deterministic policy evaluation with default-deny fallback before execution. We formalize the runtime decision model and state scoped safety properties for capability confinement and deterministic policy mediation.

We evaluate this model with a reproducible adversarial benchmark across attack families, difficulty levels, baselines, and ablations, reporting security effectiveness, latency overhead, and decision-trace quality. The practical significance is a research-grounded enforcement layer for tool-using agents that supports auditable deployment decisions without claiming general AI safety.

## Links
- [FORMAL_MODEL](FORMAL_MODEL.md)
- [THREAT_MODEL](THREAT_MODEL.md)
- [METRICS](METRICS.md)
- [RESULTS](results_tables.md)
- [ROBUSTNESS](ROBUSTNESS.md)
