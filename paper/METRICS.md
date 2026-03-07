# Metrics

This section defines publication-facing metrics for baseline and ablation comparisons.

## Notation

- \(s\): system condition (baseline or ablation mode)
- \(f\): attack family
- \(d\): difficulty level (`easy`, `medium`, `hard/multi_step`)
- \(\mathcal{A}_{s,f,d}\): adversarial tasks in slice \((s,f,d)\)
- \(\mathcal{R}_{s,f,d}\): requests/decisions in slice \((s,f,d)\)

## Primary Metrics

### 1) Attack Block Rate (ABR)
Fraction of adversarial tasks blocked (deny/no-success outcome):

\[
\mathrm{ABR}(s,f,d)=
\frac{\#\{\text{blocked tasks in }\mathcal{A}_{s,f,d}\}}
{\#\{\text{tasks in }\mathcal{A}_{s,f,d}\}}
\]

Higher is better (ideal: \(1\)).

### 2) Attack Success Rate (ASR)
Fraction of adversarial tasks that achieve attacker-success outcome:

\[
\mathrm{ASR}(s,f,d)=
\frac{\#\{\text{successful attack tasks in }\mathcal{A}_{s,f,d}\}}
{\#\{\text{tasks in }\mathcal{A}_{s,f,d}\}}
\]

Lower is better (ideal: \(0\)).

For binary block-vs-success task labeling, \(\mathrm{ASR}=1-\mathrm{ABR}\).

### 3) Latency Overhead
Decision latency overhead relative to a reference system \(s_0\):

\[
\Delta \mathrm{Latency}_{pX}(s,f,d)=
\mathrm{Latency}_{pX}(s,f,d)-\mathrm{Latency}_{pX}(s_0,f,d)
\]

where \(pX \in \{p50,p95,p99\}\).

Lower overhead is better.

### 4) Trace Completeness Rate (TCR)
Let \(F_{\text{trace}}\) be required trace fields. Then:

\[
\mathrm{TCR}(s,f,d)=
\frac{\#\{r \in \mathcal{R}_{s,f,d}: r\ \text{contains all}\ F_{\text{trace}}\}}
{\#\{\mathcal{R}_{s,f,d}\}}
\]

Higher is better (ideal: \(1\)).

### 5) Explainability / Structured Decision Artifact Coverage (SDAC)
Let \(F_{\text{decision}}\) be required structured decision fields (for example `decision`, `rule_id`, `reason_code`, trace metadata). Then:

\[
\mathrm{SDAC}(s,f,d)=
\frac{\#\{r \in \mathcal{R}_{s,f,d}: r\ \text{contains all}\ F_{\text{decision}}\}}
{\#\{\mathcal{R}_{s,f,d}\}}
\]

Higher is better.

## Secondary Metrics

- **Policy decision correctness**:
  \[
  \frac{\#(\text{decisions matching expected labels})}{\#(\text{decisions})}
  \]
- **Unsafe Execution Rate (UER)**:
  \[
  \mathrm{UER}=\frac{\#(\text{expected deny but allowed})}{\#(\text{expected deny})}
  \]
- **Reason-code coverage**: fraction of deny outcomes with non-empty/non-unknown `reason_code`.
- **Deterministic explanation stability**: repeated fixed-input runs producing identical decision artifact tuples.

## Reporting Requirements

Primary metrics are reported:

1. by system condition,
2. by attack family,
3. by difficulty level,
4. and as aggregate summary.

Each reported row should include:
- point estimate (mean),
- confidence interval (per [APPENDIX_STATS](APPENDIX_STATS.md)),
- delta vs reference system.
