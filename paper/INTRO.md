# Introduction

## Problem
Tool-augmented agents can execute filesystem/network/plugin actions directly, so runtime misbehavior becomes a safety and reliability incident rather than a pure prompt-quality issue.

## Gap
Existing approaches often provide either access control, sandboxing, or prompt-level defenses, but rarely combine deterministic runtime enforcement semantics with explainable deny outputs and causal ablation-based evaluation.

## Contributions
- Deterministic runtime capability gating with explicit `rule_id` and `reason_code`.
- Formal semantics and invariants for determinism, default deny, and isolation boundaries.
- Causal ablation framework over policy gating, isolation, and trace completeness controls.
- Reproducible benchmark matrix with statistical reporting and canonical paper artifacts.

## Why now
Tool-using agent systems are rapidly moving into production settings, but evaluation standards for runtime safety controls remain under-specified and difficult to reproduce.

## Paper Roadmap
We formalize the model and threat assumptions, define metrics and protocol, and then report robustness/performance tradeoffs with reproducible artifacts.

## Links
- [FORMAL_MODEL](FORMAL_MODEL.md)
- [THREAT_MODEL](THREAT_MODEL.md)
- [METRICS](METRICS.md)
- [RESULTS](results_tables.md)
- [ROBUSTNESS](ROBUSTNESS.md)
- [PERF](PERF_DAYXX.md)
