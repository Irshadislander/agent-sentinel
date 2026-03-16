# Abstract

Tool-using agents can trigger filesystem, network, and shell side effects, so security depends on runtime authorization at the tool boundary rather than prompt quality alone. Existing defenses emphasize prompt filtering, orchestration, or isolation, but often lack deterministic request-level capability mediation with explicit audit semantics.

Agent-Sentinel introduces deterministic runtime capability gating: each tool request is evaluated by ordered policy rules with default-deny fallback before execution. We formalize this mediation model and state scoped runtime properties (including confinement, monotonicity, and composability) under explicit trust assumptions.

Evaluation combines a reproducible adversarial benchmark (attack families, difficulty levels, baselines, and ablations) with a minimal real-agent integration case study. We report security outcomes, latency overhead, and decision-trace quality from generated artifacts. The practical significance is a bounded, auditable control layer for deploying tool-using agents without claiming end-to-end AI safety.

## Links
- [FORMAL_MODEL](FORMAL_MODEL.md)
- [THREAT_MODEL](THREAT_MODEL.md)
- [METRICS](METRICS.md)
- [RESULTS](tables/results_tables.md)
- [ROBUSTNESS](ROBUSTNESS.md)
