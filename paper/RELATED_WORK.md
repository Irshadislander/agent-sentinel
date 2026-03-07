# Related Work

## Positioning Table

| Approach family | Runtime tool mediation | Deterministic policy decision | Scoped formal safety property | Explainable decision artifacts | Reproducible adversarial benchmark |
|---|---|---|---|---|---|
| Prompt guardrails / prompt-injection defenses | No (upstream) | No | Rare/limited | Partial | Partial |
| General agent runtime infrastructure | Partial | Partial | Rare/limited | Partial | Rare/limited |
| Sandboxing / isolation systems | Partial (post-execution containment) | Partial | Partial | Limited | Limited |
| Policy systems (generic access control) | Partial (not agent-specific runtime path) | Partial | Partial | Partial | Rare/limited |
| **Agent-Sentinel (this work)** | **Yes** | **Yes** | **Yes (runtime-scoped)** | **Yes** | **Yes** |

## Prompt Guardrails
Prompt-level defenses focus on input/output filtering and instruction conflict handling. They are complementary, but they do not by themselves enforce capability authorization at the moment of tool execution.

## Runtime Infrastructure
Agent runtimes provide orchestration and tool abstraction, but often do not define deterministic, formally scoped mediation semantics as the primary research object. Agent-Sentinel contributes this mediation layer and its evaluation framing.

## Sandboxing and Isolation
Sandboxing limits damage after code or tool execution starts. Agent-Sentinel addresses an earlier point in the control path: pre-execution authorization with explicit deny semantics. The two are complementary, not interchangeable.

## Policy Systems
Generic policy systems provide access-control abstractions, but may not target tool-using agent request semantics, adversarial prompt-to-tool transitions, or decision-artifact reproducibility under benchmark stress.

## Reviewer-Facing Positioning
Agent-Sentinel is positioned as a systems-security research contribution on deterministic runtime capability mediation for agent tool use. Its novelty is the combination of formalized runtime semantics, scoped safety properties, and reproducible adversarial evaluation, not a claim of end-to-end AI safety.
