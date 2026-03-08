# Conclusion

Agent-Sentinel frames tool-use security as a runtime mediation problem: authorize each tool request deterministically at the execution boundary, then emit auditable decision evidence. The core contribution is a capability-based default-deny enforcement model with scoped formal properties (including monotonicity and composability) under explicit trust assumptions.

Evaluation combines a reproducible adversarial benchmark (families, difficulty levels, baselines, and ablations) with a minimal real-agent integration case study. Together, these artifacts provide measurable evidence on security outcomes, runtime overhead, and trace quality without overstating coverage.

The practical takeaway is that runtime capability mediation can be deployed as a concrete control point in tool-using agent stacks, complementing guardrails and sandboxing in defense-in-depth designs. The scientific takeaway is that tool-use safety can be studied as a reproducible systems-security problem with explicit scope and falsifiable claims.

Future work includes broader workload coverage, stronger policy-authoring support, and deeper evaluation in production-oriented agent frameworks.

## Links
- [FORMAL_MODEL](FORMAL_MODEL.md)
- [THREAT_MODEL](THREAT_MODEL.md)
- [METRICS](METRICS.md)
- [RESULTS](results_tables.md)
- [RELATED_WORK](RELATED_WORK.md)
