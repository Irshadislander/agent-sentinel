# Introduction

Tool-augmented agents are increasingly connected to high-impact tools such as filesystems, network endpoints, and shell-like execution surfaces. In this setting, unsafe tool calls become runtime security failures. The core systems problem is enforcing least privilege deterministically before side effects occur.

Existing defenses provide useful but partial coverage. Prompt-level guardrails are probabilistic, sandboxing is necessary but not sufficient for request-level authorization, and generic runtime infrastructure does not always provide deterministic decision semantics with explainable outputs. What is often missing is a unified runtime enforcement layer that is formally scoped and reproducibly evaluated under adversarial conditions.

Agent-Sentinel addresses this gap with deterministic runtime capability gating at the tool boundary. Each tool request is evaluated against ordered policy rules with default deny fallback; tool execution proceeds only on allow. The system emits structured decision artifacts (`decision`, `rule_id`, `reason_code`, trace metadata) to support auditing and debugging. We pair this implementation with a formal model, explicit threat assumptions, and a benchmark-style adversarial evaluation protocol.

## Contributions
- Deterministic runtime capability-gating model for tool-augmented agents at the request-to-tool boundary.
- Runtime-scoped formal safety framing for policy-based enforcement behavior and capability confinement.
- Reproducible adversarial evaluation design with baseline and ablation conditions over defined attack families and difficulty levels.
- Explainable decision artifacts and trace outputs suitable for operational auditing and incident analysis.
- End-to-end artifact workflow connecting run outputs to reporting tables.

## Paper Structure
Section 2 presents the method and enforcement pipeline. Section 3 formalizes the capability and policy model. Sections 4-6 define threat assumptions, metrics, and evaluation protocol. Section 7 reports experimental and ablation results. We conclude with deployment implications, limitations, and future directions.

## Scope
This paper focuses on runtime tool-use enforcement and observability. It does not claim comprehensive or general AI safety.

## Links
- [FORMAL_MODEL](FORMAL_MODEL.md)
- [THREAT_MODEL](THREAT_MODEL.md)
- [METRICS](METRICS.md)
- [RESULTS](results_tables.md)
- [ROBUSTNESS](ROBUSTNESS.md)
- [PERF](PERF_DAYXX.md)
