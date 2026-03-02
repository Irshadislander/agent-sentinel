# Introduction

Tool-using agent systems are difficult to secure and debug because execution authority is spread across planners, runtime gateways, and extension surfaces such as plugins. Prompt injection and payload poisoning can redirect tool calls toward unsafe actions, plugin behavior can violate expected contracts, and failure reporting is often inconsistent across components. These properties complicate both enforcement and post-incident analysis.

Existing agent infrastructures frequently emphasize capability breadth and orchestration flexibility, but they do not consistently operationalize safety and reliability as quantitative properties with reproducible measurement. As a result, it is difficult to determine whether a runtime control improves security guarantees or simply changes implementation style.

This paper makes the following contributions:
- A formal capability-execution model with explicit enforcement semantics and deterministic outcome classes.
- A metric framework (UER, FAR, TCR, EDS, PEA) that maps directly to runtime and benchmark artifacts.
- A controlled ablation protocol using baseline toggles (`no_policy`, `no_trace`, `raw_errors`, `no_plugin_isolation`) to isolate causal effects of controls.
- An adversarial task suite designed to expose safety/reliability deltas under realistic failure modes.
- A reproducible evaluation pipeline that generates machine-readable matrix outputs and paper-ready summary tables.

The paper proceeds from problem formalization and threat boundaries to method and metric definitions, then details the evaluation protocol and experiments, followed by quantitative results, threat-model discussion, and related-work positioning.
