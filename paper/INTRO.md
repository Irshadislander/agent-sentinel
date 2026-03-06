# Introduction

## Problem
Tool-augmented agents are no longer text-only interfaces: they issue executable calls into filesystems, HTTP endpoints, and plugin surfaces. A single unsafe tool invocation can become a runtime security incident. The central systems question is whether the runtime can enforce least privilege deterministically before side effects occur.

## Gap in Existing Work
Current defenses are split across prompt-level safeguards, sandboxing, and generic policy/runtime infrastructure. These are useful components, but the combination is often missing: deterministic runtime tool gating, formal safety properties of the gate, explainable decision outputs, and reproducible adversarial evaluation that isolates control-level effects.

## Our Approach
Agent-Sentinel treats runtime authorization as a first-class enforcement layer. Every tool request passes through capability gating with explicit policy resolution and default deny. The runtime emits structured decision artifacts (`decision`, `rule_id`, `reason_code`, trace metadata), enabling machine-auditable explanations of why requests were allowed or denied. We pair the implementation with a formal model and adversarial ablation protocol.

## Contributions
1. Deterministic runtime capability-gating model for tool-augmented agents at the tool boundary.
2. Formal safety properties for that model, including determinism and default-deny behavior under missing/invalid policy inputs.
3. Causal, reproducible adversarial evaluation using targeted ablations (`no_policy`, `no_trace`, `raw_errors`, `no_plugin_isolation`).
4. Explainable trace/audit outputs with explicit decision fields (`rule_id`, `reason_code`, trace metadata).
5. Reproducible artifact pipeline from benchmark outputs to paper tables.

## Why Now
Production agent systems are rapidly increasing their access to high-impact tools. As this access expands, safety claims based on anecdotal demos are insufficient. Deterministic enforcement plus artifact-backed adversarial evaluation makes runtime safety behavior testable and reproducible.

## Scope
This paper is scoped to runtime tool-use enforcement and auditability. It does not claim comprehensive or general AI safety.

## Paper Roadmap
We formalize the model and threat assumptions, define metrics and protocol, and report safety-observability-performance tradeoffs using reproducible artifacts.

## Links
- [FORMAL_MODEL](FORMAL_MODEL.md)
- [THREAT_MODEL](THREAT_MODEL.md)
- [METRICS](METRICS.md)
- [RESULTS](results_tables.md)
- [ROBUSTNESS](ROBUSTNESS.md)
- [PERF](PERF_DAYXX.md)
