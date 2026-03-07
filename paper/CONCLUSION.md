# Conclusion

This paper contributes a research-focused formulation of runtime security for tool-using AI agents: capability-based enforcement with deterministic policy mediation at the request-to-tool boundary. The core scientific contribution is not a product stack, but a formalized runtime mediation model with scoped safety properties and auditable decision outputs.

We pair this model with reproducible adversarial evaluation across attack families, difficulty levels, baselines, and ablations, enabling direct measurement of security effectiveness, overhead, and observability tradeoffs. This positions runtime tool-use safety as a testable systems question rather than a qualitative guardrail narrative.

Why this matters is practical and scientific: deployment decisions require enforceable runtime controls, and research claims require reproducible evidence and explicit scope. Agent-Sentinel contributes both under clearly bounded assumptions.

Future work includes broader workload coverage, deeper analysis of policy-authoring quality, and expanded scaling studies under heterogeneous runtime conditions. These directions extend the benchmark and mediation analysis without expanding claims beyond runtime enforcement scope.

## Links
- [FORMAL_MODEL](FORMAL_MODEL.md)
- [THREAT_MODEL](THREAT_MODEL.md)
- [METRICS](METRICS.md)
- [RESULTS](results_tables.md)
- [RELATED_WORK](RELATED_WORK.md)
