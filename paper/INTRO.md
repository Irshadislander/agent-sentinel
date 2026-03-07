# Introduction

## Problem
Tool-augmented agents are increasingly connected to high-impact execution surfaces (filesystem, network, shell, and external tools). In this setting, unsafe tool invocation is a runtime systems-security failure with immediate side effects.

## Gap in Existing Work
Prior work offers important but partial defenses: prompt guardrails are often probabilistic, runtime infrastructure focuses on orchestration, and sandboxing limits blast radius after execution begins. What is frequently missing is a deterministic, capability-based authorization layer at the request-to-tool boundary with formalized behavior and reproducible evaluation.

## Research Focus
This paper studies runtime capability enforcement as a research problem: given a tool request, policy, and capability map, can the runtime deterministically mediate execution and emit auditable decision artifacts? Agent-Sentinel answers this with policy-mediated, default-deny gating before tool side effects, coupled to a formal model and benchmark-driven evaluation.

## Contributions
- A capability-based runtime enforcement model for tool-using agents with deterministic policy mediation.
- Runtime-scoped safety properties under stated trust assumptions, including monotonicity, capability confinement, and scoped policy composability.
- A reproducible adversarial benchmark design spanning attack families, difficulty levels, baselines, and ablations.
- Structured decision artifacts (`decision`, `rule_id`, `reason_code`, trace metadata) for explainable, machine-auditable runtime behavior.
- An artifact pipeline that connects benchmark outputs to paper-facing tables and figure guidance.

## Why This Matters
This work frames secure agent execution as a measurable systems question rather than a product feature claim. It provides a narrow, testable contribution: deterministic runtime enforcement and auditable decision semantics for tool use, not general AI safety.

## Production Agent Relevance
The enforcement interface studied here is intentionally runtime-facing and maps to common tool-call boundaries in modern agent stacks. This makes the framework directly relevant to:
- LangChain-style tool agents,
- OpenAI tool-calling runtimes,
- multi-agent orchestration systems.

The claim is applicability of the mediation model, not evidence of broad production deployment.

## Links
- [FORMAL_MODEL](FORMAL_MODEL.md)
- [THREAT_MODEL](THREAT_MODEL.md)
- [METRICS](METRICS.md)
- [RESULTS](results_tables.md)
- [RELATED_WORK](RELATED_WORK.md)
