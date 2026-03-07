# Conclusion

Agent-Sentinel frames runtime tool safety as a deterministic authorization problem at the tool boundary. The main contribution is a capability-gating enforcement layer that evaluates policy before execution, applies default-deny behavior, and emits structured decision artifacts for every request.

This design is paired with a formal runtime model and evaluated using reproducible adversarial workloads with baseline and ablation conditions. The result is a measurable comparison framework across security effectiveness, latency overhead, and trace quality, rather than qualitative guardrail narratives.

The security implication is practical: reliable tool-using agents need enforceable runtime controls and auditable decisions under explicit trust assumptions. Agent-Sentinel contributes this layer without claiming general AI safety.

Future work includes broader workload coverage, deeper analysis of policy-authoring quality, and expanded deployment studies for high-throughput environments and heterogeneous agent runtimes.

## Links
- [FORMAL_MODEL](FORMAL_MODEL.md)
- [THREAT_MODEL](THREAT_MODEL.md)
- [METRICS](METRICS.md)
- [RESULTS](results_tables.md)
- [ROBUSTNESS](ROBUSTNESS.md)
- [PERF](PERF_DAYXX.md)
