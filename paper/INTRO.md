# Introduction

## Problem
Tool-using agents are increasingly connected to high-impact execution surfaces such as filesystem, network, and shell interfaces. In this setting, unsafe behavior is a runtime authorization failure with immediate side effects, not only a low-quality model response.

This threat model differs from plain chat LLM systems. Chat-only systems primarily emit text, while tool-using systems transform model output into executable operations against external state.

## Gap in Existing Work
Prior defenses are important but partial in isolation: prompt guardrails are often probabilistic, orchestration frameworks focus on workflow composition, and sandboxing constrains damage after execution starts. What is frequently missing is deterministic authorization at the request-to-tool boundary itself.

## Our Focus
We study runtime capability mediation as a systems-security problem: given a tool request, policy, and capability map, can the runtime deterministically allow or deny execution and emit auditable evidence? Agent-Sentinel addresses this with ordered policy evaluation, explicit default-deny behavior, and structured decision artifacts before tool side effects occur.

## Contributions
- A deterministic capability-based runtime mediation model for tool-using agents.
- Scoped formal properties under explicit trust assumptions, including monotonicity, capability confinement, and policy composability.
- A reproducible benchmark protocol spanning attack families, difficulty levels, baselines, and ablations.
- A minimal real-agent integration case study demonstrating request-to-decision mediation through the runtime gateway.
- An artifact pipeline that maps benchmark outputs to paper-facing tables and figures.

## Scope
This paper contributes bounded runtime security and observability guarantees. It does not claim general AI safety or complete system security.

## Production Agent Relevance
The mediation interface is runtime-facing and aligns with common tool-call boundaries in:
- LangChain-style tool agents,
- OpenAI tool-calling runtimes,
- multi-agent orchestration systems.

The claim is framework applicability of the mediation model, not evidence of broad production deployment.

## Links
- [FORMAL_MODEL](FORMAL_MODEL.md)
- [THREAT_MODEL](THREAT_MODEL.md)
- [METRICS](METRICS.md)
- [RESULTS](tables/results_tables.md)
- [RELATED_WORK](RELATED_WORK.md)
