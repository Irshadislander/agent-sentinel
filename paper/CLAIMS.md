# Contributions (Camera-Ready)

**C1. Deterministic runtime capability-gating model.**  
We define and implement a runtime gating model that resolves capability requests before tool execution under explicit policy and default-deny fallback.

**C2. Formal safety properties for runtime enforcement.**  
We formalize key invariants of the gate, including deterministic outcomes and deny-on-missing/invalid-policy behavior.

**C3. Causal, reproducible adversarial evaluation protocol.**  
We evaluate targeted ablations (`no_policy`, `no_trace`, `raw_errors`, `no_plugin_isolation`) to isolate control-level effects on safety, observability, and performance.

**C4. Explainable trace and audit outputs.**  
We emit structured decision artifacts (`decision`, `rule_id`, `reason_code`, trace metadata/commitment) that support machine-auditable runtime explanations.

**C5. Reproducible artifact pipeline.**  
We provide deterministic benchmark/report scripts and fixed artifact conventions to regenerate paper-facing outputs from repository results.

## Scope Boundary
These claims are specific to runtime tool-use enforcement and auditability. They are not claims of general AI safety.
