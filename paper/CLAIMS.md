# Contributions (Camera-ready)

**C1. Deterministic Safety Resolution.** We introduce a deterministic rule-resolution policy engine that returns (decision, rule_id, reason_code, evaluation_trace, duration_ms) under well-defined precedence.

**C2. Formal Semantics + Verifiable Invariants.** We formalize decision semantics and provide invariants (determinism, default-deny safety, isolation boundary) with proof sketches aligned with implementation.

**C3. Robustness Evaluation Axis.** We demonstrate robustness under concrete attack-scenario tests (bypass/override/trace suppression) and report attack success and trace integrity metrics.

**C4. Performance + Stress Axis.** We provide a microbenchmark suite producing p50/p95/p99 latency under stress configurations, with reproducible artifact outputs.

**C5. Reproducible Evaluation Pipeline.** We release a one-command pipeline that regenerates canonical reports and paper tables from benchmark artifacts.
