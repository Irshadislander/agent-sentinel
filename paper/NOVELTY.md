# Novelty

## One-sentence novelty claim
We provide a **deterministic, auditable runtime policy engine** for tool-augmented agents and a **reproducible causal ablation harness** that quantifies safety, observability, robustness, and latency trade-offs.

## What existing papers/systems do NOT provide
- Deterministic decision semantics with stable **reason codes + trace semantics** tied to a formal model.
- A reproducible harness that isolates the causal impact of runtime controls via explicit ablations.
- Attack-scenario robustness tests linked to metrics and paper tables.

## What we uniquely provide
- Open implementation: deterministic resolver (decision, rule_id, reason_code, trace, duration).
- Benchmarks: latency distribution + stress axis; robustness axis via attack scenario tests.
- Canonical report generator that produces paper-ready tables from artifacts.
