# Related Work

## Security-Angle Mini-Table

| Work/System | Runtime tool gating | Explainable decisions (`rule_id`/`reason_code`) | Reproducible causal ablations | Trace completeness metric |
|---|---:|---:|---:|---:|
| OPA-style policy engines | △ | ✗ | ✗ | ✗ |
| Sandbox systems (container/WASM) | △ | ✗ | ✗ | ✗ |
| Prompt-injection defense papers | ✗ | ✗ | △ | ✗ |
| **Agent-Sentinel (this work)** | **✓** | **✓** | **✓** | **✓** |

Legend: ✓ direct support, △ partial/adjacent support, ✗ not a core feature.

## Gap Paragraph (non-negotiable)

Prior systems provide useful components (policy evaluation, sandbox isolation, or prompt-side mitigations), but typically not a single runtime framework that jointly provides deterministic tool gating, explainable decision outputs, causal ablations, and explicit trace-completeness measurement. Agent-Sentinel targets this intersection with formal semantics and artifact-backed evaluation under controlled adversarial workloads.
