# Metrics (Final)

This section defines final publication-facing metrics.

## 1. Security Effectiveness

- **Attack Block Rate (ABR)**: \(\mathrm{ABR}=\#\text{blocked attacks}/\#\text{attacks}\)
- **Attack Success Rate (ASR)**: \(\mathrm{ASR}=\#\text{successful attacks}/\#\text{attacks}\)

For binary labels, \(\mathrm{ASR}=1-\mathrm{ABR}\).

## 2. Performance

- **Median latency overhead**: p50 decision-latency delta vs reference.
- **Tail latency overhead**: p95 and p99 latency deltas vs reference.
- **Throughput**: processed requests per second.
- **Scaling behavior**: throughput/latency changes as workload size increases.

Representative definitions:
\[
\Delta \mathrm{Latency}_{pX} = \mathrm{Latency}_{pX}(s)-\mathrm{Latency}_{pX}(s_0),\quad pX\in\{p50,p95,p99\}
\]
\[
\mathrm{Throughput}(s)=\frac{\#\text{processed requests}}{\text{time}}
\]

## 3. Observability / Trace Quality

- **Trace Completeness Rate (TCR)**: fraction of decisions containing required trace fields.
- **Structured Decision Artifact Coverage (SDAC)**: fraction of decisions containing required decision-artifact fields.

## 4. Reporting Rules

Each reported table row should include:
- point estimate,
- 95% confidence interval,
- delta versus declared reference.

All metrics are aggregated from benchmark matrix outputs (family × difficulty × baseline).
