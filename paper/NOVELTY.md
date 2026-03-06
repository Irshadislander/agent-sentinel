# Novelty

## Niche Claim
Agent-Sentinel targets a specific niche: deterministic runtime capability-gating for tool-augmented agents with formal safety properties and reproducible adversarial evaluation.

## Scientific Novelty (Beyond Framework Assembly)
1. **Deterministic enforcement semantics as a formal object.** We specify runtime decision behavior over capability requests and policy inputs, including stable deny outcomes.
2. **Property-driven safety characterization.** We define scoped invariants for determinism, default-deny safety, and gateway mediation, rather than relying only on qualitative examples.
3. **Causal control-level evaluation.** We use targeted ablations (`no_policy`, `no_trace`, `raw_errors`, `no_plugin_isolation`) to attribute metric shifts to specific runtime controls.
4. **Explainability tied to enforcement outputs.** Decisions are emitted with structured audit fields (`rule_id`, `reason_code`, trace metadata), enabling reproducible diagnosis of runtime behavior.
5. **Reproducible artifact pipeline.** Benchmark outputs and scripts regenerate reporting artifacts directly from repository workflows.

## Boundaries of the Claim
- We do not claim complete protection against all attack classes.
- We do not claim general AI safety; claims are restricted to runtime tool-use enforcement and auditability within the stated threat model.
