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

## LLM Alignment Approaches
Alignment-focused methods target model behavior at training or inference time and can reduce unsafe generations, but they are not a substitute for explicit runtime authorization at the tool boundary. Agent-Sentinel is scoped to deterministic runtime mediation rather than model-internal alignment.

## Runtime Infrastructure and Orchestration Frameworks
Agent runtimes and orchestration frameworks provide planning loops, tool adapters, and state management. These systems are operationally important, but orchestration by itself does not guarantee deterministic allow/deny capability mediation for each request.

## Sandboxing and Isolation
Sandboxing limits damage after code or tool execution starts. Agent-Sentinel addresses an earlier point in the control path: pre-execution authorization with explicit deny semantics. The two are complementary, not interchangeable.

## Policy Systems
Generic policy systems provide access-control abstractions, but may not target tool-using agent request semantics, adversarial prompt-to-tool transitions, or decision-artifact reproducibility under benchmark stress.

## Production Agent Relevance
Agent-Sentinel is positioned as a complementary enforcement layer for production-oriented stacks, including LangChain-style tool agents, OpenAI tool-calling runtimes, and multi-agent orchestration systems. The contrast with prior work is that runtime capability mediation is treated as the primary research object with explicit deny semantics and reproducible benchmarking, without claiming deployed production coverage.

## Reviewer-Facing Positioning
Agent-Sentinel is positioned as a systems-security research contribution on deterministic runtime capability mediation for agent tool use. Its novelty is the combination of formalized runtime semantics, scoped safety properties, and reproducible adversarial evaluation, not a claim of end-to-end AI safety.
