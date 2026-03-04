# Novelty

## One-sentence novelty claim
We introduce a deterministic runtime capability-gating model for tool-augmented agents and provide a causal evaluation of safety-observability-extensibility tradeoffs under controlled adversarial workloads.

## What prior work lacks
- Deterministic enforcement semantics, causal ablations, and a trace-completeness metric in one unified harness.
- Explainable deny outcomes (`rule_id`, `reason_code`) tied to formal runtime resolution semantics.
- Reproducible matrix execution that isolates control-level effects under adversarial workloads.

## What we provide
- Formal model plus invariants for deterministic runtime capability gating and default deny.
- Causal ablation framework isolating policy gating, plugin/tool isolation, and trace completeness.
- Reproducible benchmark matrix and explainable decision artifacts suitable for paper-grade reporting.
