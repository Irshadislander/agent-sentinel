# Abstract

## Problem
Tool-augmented agents can trigger filesystem, network, and plugin actions with real side effects. In this setting, safety depends on runtime enforcement at the tool boundary, not only on prompt quality.

## Why Existing Work Is Insufficient
Nearby approaches usually focus on one layer at a time (prompt guardrails, sandboxing, or policy infrastructure). They often do not provide a unified runtime mechanism that is deterministic, formally specified, and evaluated through reproducible adversarial ablations.

## What Agent-Sentinel Introduces
Agent-Sentinel provides deterministic runtime capability-gating for tool-augmented agents. Requests are resolved before tool execution with default-deny fallback, and decisions emit structured evidence (`decision`, `rule_id`, `reason_code`, trace metadata) for explainability and audit.

## What We Prove and Evaluate
We formalize the decision model and scoped safety properties (determinism, default-deny safety, gateway-mediated enforcement boundary). We evaluate benign and adversarial workloads with controlled ablations (`no_policy`, `no_trace`, `raw_errors`, `no_plugin_isolation`) to isolate effects on safety, observability, and performance.

## Reproducibility and Artifacts
We provide formal-model and threat-model documents, matrix benchmark outputs, and canonical report-generation scripts so results can be regenerated from repository artifacts.

## Scope
This paper addresses runtime tool-use enforcement and auditability; it does not claim general AI safety.

## Links
- [FORMAL_MODEL](FORMAL_MODEL.md)
- [THREAT_MODEL](THREAT_MODEL.md)
- [METRICS](METRICS.md)
- [RESULTS](results_tables.md)
- [ROBUSTNESS](ROBUSTNESS.md)
- [PERF](PERF_DAYXX.md)
