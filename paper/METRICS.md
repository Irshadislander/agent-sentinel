# Metrics

This section defines publication-facing metrics for baseline and ablation comparisons.

## Primary Comparison Metrics (Reviewer View)

| Metric | Definition | Direction |
|---|---|---|
| **Attack Block Rate (ABR)** | fraction of adversarial tasks blocked | higher is better |
| **Attack Success Rate (ASR)** | fraction of adversarial tasks that succeed | lower is better |
| **Latency Overhead** | added decision latency vs reference mode (`full_system`) | lower is better |
| **Trace Completeness (TCR)** | fraction of decisions containing required trace fields | higher is better |
| **Decision Artifact Coverage (SDAC)** | fraction of decisions containing required structured explainability fields | higher is better |

These are the primary metrics for all baseline comparison tables.

## Notation

- \(s\): system condition (baseline or ablation mode)
- \(f\): attack family
- \(d\): difficulty level (`easy`, `medium`, `hard/multi_step`)
- \(\mathcal{A}_{s,f,d}\): adversarial tasks in slice \((s,f,d)\)
- \(\mathcal{R}_{s,f,d}\): requests/decisions in slice \((s,f,d)\)

## Formal Definitions

### 1) Attack Block Rate (ABR)
\[
\mathrm{ABR}(s,f,d)=
\frac{\#\{\text{blocked tasks in }\mathcal{A}_{s,f,d}\}}
{\#\{\text{tasks in }\mathcal{A}_{s,f,d}\}}
\]

### 2) Attack Success Rate (ASR)
\[
\mathrm{ASR}(s,f,d)=
\frac{\#\{\text{successful attack tasks in }\mathcal{A}_{s,f,d}\}}
{\#\{\text{tasks in }\mathcal{A}_{s,f,d}\}}
\]

For binary task labeling, \(\mathrm{ASR}=1-\mathrm{ABR}\).

### 3) Latency Overhead
\[
\Delta \mathrm{Latency}_{pX}(s,f,d)=
\mathrm{Latency}_{pX}(s,f,d)-\mathrm{Latency}_{pX}(s_0,f,d)
\]

where \(s_0\) is the reference system and \(pX \in \{p50,p95,p99\}\).

### 4) Trace Completeness Rate (TCR)
Let \(F_{\text{trace}}\) be required trace fields.
\[
\mathrm{TCR}(s,f,d)=
\frac{\#\{r \in \mathcal{R}_{s,f,d}: r\ \text{contains all}\ F_{\text{trace}}\}}
{\#\{\mathcal{R}_{s,f,d}\}}
\]

### 5) Structured Decision Artifact Coverage (SDAC)
Let \(F_{\text{decision}}\) be required structured decision fields (for example `decision`, `rule_id`, `reason_code`, trace metadata).
\[
\mathrm{SDAC}(s,f,d)=
\frac{\#\{r \in \mathcal{R}_{s,f,d}: r\ \text{contains all}\ F_{\text{decision}}\}}
{\#\{\mathcal{R}_{s,f,d}\}}
\]

## Baseline Reporting Requirements
For each baseline row, report:
- point estimate for ABR, ASR, latency overhead (p50/p95/p99), TCR, SDAC,
- confidence interval,
- delta vs `full_system`.

## Secondary Metrics (Optional)
- Policy decision correctness.
- Unsafe execution rate (expected deny but allowed).
- Reason-code coverage among deny outcomes.
- Explanation stability under repeated fixed-input runs.
