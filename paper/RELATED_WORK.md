# Related Work

## Comparison Table

| Work/System | Runtime gating | Plugin isolation | Trace completeness metric | Causal ablations | Reproducible harness |
|---|---:|---:|---:|---:|---:|
| Prior Work A (Tool safety) | ✓ | ✗ | ✗ | ✗ | △ |
| Prior Work B (Policy guardrails) | △ | ✗ | ✗ | ✗ | ✗ |
| Prior Work C (Audit/logging) | ✗ | ✗ | △ | ✗ | △ |
| **Agent-Sentinel (this work)** | **✓** | **✓** | **✓** | **✓** | **✓** |

Legend: ✓ supported, △ partial/indirect, ✗ not provided.

## Gap Paragraph (non-negotiable)

The strongest prior systems demonstrate tool-use safety via prompt constraints, heuristic guardrails, or access control primitives, but they do not provide a unified, deterministic policy resolution model with stable reason codes and measurable trace completeness, nor do they isolate the causal effect of runtime safety controls via reproducible ablations. Agent-Sentinel fills this gap by formalizing deterministic semantics, enforcing tool gateway isolation, and releasing a canonical evaluation pipeline with explicit ablation axes for robustness, observability, and latency.
