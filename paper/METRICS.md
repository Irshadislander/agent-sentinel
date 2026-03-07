# Metrics

This section defines benchmark metrics for security effectiveness, performance cost, and observability quality.

## Metric Categories

### Security Effectiveness Metrics
- **Attack Block Rate (ABR)**: fraction of adversarial tasks blocked.
- **Attack Success Rate (ASR)**: fraction of adversarial tasks that succeed.

### Performance Metrics
- **Median latency overhead**: decision-latency delta at p50 relative to reference.
- **Tail latency overhead**: decision-latency deltas at p95 and p99.
- **Throughput / request handling rate**: requests processed per second.
- **Scaling behavior**: latency and throughput behavior as workload size increases.

### Observability / Trace Metrics
- **Trace Completeness Rate (TCR)**: fraction of decisions containing required trace fields.
- **Structured Decision Artifact Coverage (SDAC)**: fraction of decisions containing required explainability fields.

## Notation

- \(s\): system condition (baseline or ablation)
- \(f\): attack family
- \(d\): difficulty level (`easy`, `medium`, `hard/multi_step`)
- \(N\): workload size (tasks/requests)
- \(\mathcal{A}_{s,f,d}\): adversarial tasks in slice \((s,f,d)\)
- \(\mathcal{R}_{s,f,d}\): requests/decisions in slice \((s,f,d)\)

## Formal Definitions

### Security Effectiveness
\[
\mathrm{ABR}(s,f,d)=
\frac{\#\{\text{blocked tasks in }\mathcal{A}_{s,f,d}\}}
{\#\{\text{tasks in }\mathcal{A}_{s,f,d}\}}
\]

\[
\mathrm{ASR}(s,f,d)=
\frac{\#\{\text{successful attack tasks in }\mathcal{A}_{s,f,d}\}}
{\#\{\text{tasks in }\mathcal{A}_{s,f,d}\}}
\]

For binary task labeling, \(\mathrm{ASR}=1-\mathrm{ABR}\).

### Performance
Latency overhead at percentile \(pX \in \{p50,p95,p99\}\):
\[
\Delta \mathrm{Latency}_{pX}(s,f,d)=
\mathrm{Latency}_{pX}(s,f,d)-\mathrm{Latency}_{pX}(s_0,f,d)
\]
where \(s_0\) is the declared reference condition.

Throughput:
\[
\mathrm{Throughput}(s,N)=\frac{\#\text{processed requests}}{\text{wall-clock seconds}}
\]

Scaling behavior:
\[
\mathrm{ScaleThroughputRatio}(s,N)=
\frac{\mathrm{Throughput}(s,N)}{\mathrm{Throughput}(s,N_0)}
\]
\[
\mathrm{ScaleLatencyRatio}_{p95}(s,N)=
\frac{\mathrm{Latency}_{p95}(s,N)}{\mathrm{Latency}_{p95}(s,N_0)}
\]
where \(N_0\) is the smallest scale tier.

### Observability / Trace
Let \(F_{\text{trace}}\) be required trace fields and \(F_{\text{decision}}\) required decision-artifact fields.
\[
\mathrm{TCR}(s,f,d)=
\frac{\#\{r \in \mathcal{R}_{s,f,d}: r\ \text{contains all}\ F_{\text{trace}}\}}
{\#\{\mathcal{R}_{s,f,d}\}}
\]
\[
\mathrm{SDAC}(s,f,d)=
\frac{\#\{r \in \mathcal{R}_{s,f,d}: r\ \text{contains all}\ F_{\text{decision}}\}}
{\#\{\mathcal{R}_{s,f,d}\}}
\]

## Reporting Requirements
For each reported row include:
- point estimate,
- 95% confidence interval,
- delta versus reference.

Performance reporting must include p50/p95/p99 latency, throughput, and at least one scaling view under larger task sets.
