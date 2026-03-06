# Related Work

## Compact Comparison

| Approach family | Runtime tool gating | Deterministic enforcement | Formal safety property | Explainable decisions | Reproducible adversarial evaluation |
|---|---|---|---|---|---|
| Probabilistic / runtime-verification style agent guards | Partial | No | Rare/limited | Partial | Rare/limited |
| General AI runtime infrastructure / agent runtime systems | Partial | Partial | Rare/limited | Partial | Rare/limited |
| Prompt-injection / guardrail work | No | No | Rare/limited | Partial | Partial |
| Sandbox / tool isolation systems | Partial | Partial | Partial | Limited | Limited |
| **Agent-Sentinel (this work)** | **Yes** | **Yes** | **Yes (scoped invariants)** | **Yes** | **Yes** |

Legend: "Partial" indicates adjacent support but not the full end-to-end property in this paper's scope.

## Probabilistic and Runtime-Verification Guards
Probabilistic guards and runtime-verification heuristics often estimate risk or detect suspicious behavior, but their decisions may vary across runs and are not always tied to deterministic policy resolution at the tool boundary. Agent-Sentinel is positioned as deterministic runtime enforcement rather than probabilistic filtering.

## General Agent Runtime Infrastructure
Agent runtime systems typically emphasize orchestration and tool plumbing. They may host policy hooks, but often do not center formalized runtime safety properties plus ablation-based adversarial evidence. Agent-Sentinel contributes this enforcement-and-evaluation layer.

## Prompt-Injection and Guardrail Methods
Prompt-injection defenses operate upstream by shaping prompts, outputs, or model behavior. These controls are complementary but do not replace runtime authorization at the point of tool execution. Agent-Sentinel focuses on that execution boundary.

## Sandbox and Tool-Isolation Systems
Isolation systems reduce blast radius after code/tool execution begins. By themselves, they do not usually provide deterministic capability-level allow/deny decisions with explicit `rule_id`/`reason_code` outputs. Agent-Sentinel is a pre-execution policy gate that can coexist with sandboxing.

## Positioning Summary
The closest prior systems provide valuable components, but typically not the combined target of this paper: deterministic runtime capability-gating, scoped formal safety properties, explainable decision artifacts, and reproducible adversarial evaluation.
