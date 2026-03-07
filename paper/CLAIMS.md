# Contributions (Final Framing)

**C1. Capability-based runtime enforcement model.**
We define a runtime mediation model for tool requests in which execution is authorized only through capability checks and policy rules at the request boundary.

**C2. Deterministic policy mediation semantics.**
We specify deterministic decision behavior with ordered rule evaluation and default-deny fallback, making authorization outcomes stable and reproducible.

**C3. Runtime-scoped safety properties.**
We state explicit safety properties of the mediation layer under declared trust assumptions, including monotonicity, capability confinement, and scoped policy composability for deterministic default-deny mediation. These are theorem statements with proof sketches, not claims of machine-checked full verification.

**C4. Reproducible adversarial evaluation framework.**
We evaluate the enforcement model with a benchmark matrix over attack families, difficulty levels, baselines, and ablations using predeclared metrics.

**C5. Explainable decision and trace artifacts.**
We treat structured decision outputs (`decision`, `rule_id`, `reason_code`, trace metadata) as measurable research outputs for auditing and comparison.

## Scope Boundary
These claims are restricted to runtime tool-use enforcement and observability. They are not claims of general AI safety or complete system security.
