# Novelty

## Central Niche
Agent-Sentinel targets a narrow research niche: **runtime capability enforcement for tool-using AI agents** with deterministic policy mediation, scoped safety properties, and reproducible adversarial evaluation.

## Scientific Contribution (Not Product Positioning)

1. **Capability-based runtime mediation as a formal object.**
   The contribution is not “an agent platform,” but a formalized runtime decision object over `(tool, args, context)` requests, capability requirements, and ordered policy rules.

2. **Deterministic enforcement semantics.**
   Policy mediation is specified as deterministic resolution with explicit default-deny behavior, enabling repeatable security analysis across runs and workloads.

3. **Runtime-scoped safety properties.**
   We state safety properties about enforcement behavior (for example confinement and deterministic mediation) under explicit trust assumptions, rather than broad claims about model cognition.

4. **Reproducible adversarial evaluation design.**
   The evaluation is structured as a benchmark matrix (family × difficulty × baseline × metric), enabling causal interpretation of control-level changes.

5. **Explainability coupled to enforcement outputs.**
   Decision artifacts are first-class outputs of the enforcement path, supporting post-hoc auditing and empirical comparison.

## Why This Is Research
The core contribution is a falsifiable systems-security formulation with explicit properties and benchmark methodology. The paper asks and answers a research question about runtime mediation semantics, not a product adoption question.

## Boundaries
- No claim of complete or general AI safety.
- No claim that runtime enforcement replaces sandboxing, red-teaming, or broader infrastructure security.
- Claims are limited to runtime tool-use mediation and observability within the stated threat model.
