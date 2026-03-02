# Novelty

## Scientific Novelty Claims

1. **Formalized runtime capability semantics for tool-using agents**
   - The system models execution as an explicit enforcement function over policy, capability, and request context, with deterministic outputs (decision, exit class, trace artifact).

2. **Operationalized security claims with measurable invariants**
   - Safety is evaluated through explicit metrics (UER, FAR, TCR, EDS, PEA), enabling falsifiable claims rather than narrative-only evaluation.

3. **Baseline-oriented ablation design for causal interpretation**
   - Controlled baselines (`no_policy`, `no_trace`, `raw_errors`, `no_plugin_isolation`) isolate which control layer contributes to safety and observability.

4. **Traceability as a first-class runtime guarantee**
   - Each request path is designed to produce structured, machine-parseable evidence that can be aggregated into reproducible benchmark and paper tables.

5. **Research-to-engineering bridge**
   - The same artifacts drive both CI-grade regression checks and paper-grade reporting, reducing drift between implementation and evaluation claims.
