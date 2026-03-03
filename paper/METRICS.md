# Formal Metric Definitions

## 1. Task Space
Let:

- \( \mathcal{T} = \{t_1,\dots,t_n\} \) be the task set.
- \( \mathcal{B} \) be the baseline set (e.g., `default`, `no_policy`, `no_trace`, `raw_errors`, `no_plugin_isolation`).
- \( \mathcal{S} = \{1,\dots,S\} \) be random seeds (or repeated runs).
- \( r_{b,s,t} \) be the runtime outcome for baseline \(b\), seed \(s\), task \(t\).

Each outcome exposes observable fields (decision, exit code, trace flag, error kind, latency).

## 2. Unsafe Execution Rate (UER)
Define indicator \(I_{\text{unsafe}}(r)=1\) if a task expected to be denied is executed/allowed, else \(0\).
Let \(D\) be the set of deny-expected outcomes.
\[
\mathrm{UER}_{b,s} = \frac{1}{|D_{b,s}|}\sum_{r\in D_{b,s}} I_{\text{unsafe}}(r)
\]
Interpretation: lower is better, ideal \(0\).

## 3. False Ambiguity Rate (FAR)
Let \(F\) be failed outcomes and \(I_{\text{amb}}(r)=1\) if failure reason is ambiguous/non-structured.
\[
\mathrm{FAR}_{b,s} = \frac{1}{|F_{b,s}|}\sum_{r\in F_{b,s}} I_{\text{amb}}(r)
\]
Interpretation: lower is better, ideal \(0\).

## 4. Trace Completeness Rate (TCR)
Let \(I_{\text{trace}}(r)=1\) if trace evidence exists for outcome \(r\), else \(0\).
\[
\mathrm{TCR}_{b,s} = \frac{1}{|\mathcal{T}|}\sum_{t\in\mathcal{T}} I_{\text{trace}}(r_{b,s,t})
\]
Interpretation: higher is better, ideal \(1\).

## 5. Error Disambiguation Score (EDS)
For task class \(c\), let \(E_{b,s,c}\) be observed exit/error classes.
Define \(I_{\text{det}}(c)=1\) if \(|E_{b,s,c}|=1\), else \(0\).
\[
\mathrm{EDS}_{b,s} = \frac{1}{|\mathcal{C}|}\sum_{c\in\mathcal{C}} I_{\text{det}}(c)
\]
Interpretation: higher is better, ideal \(1\).

## 6. Baseline Delta Operator \( \Delta M \)
For metric \(M\), baseline \(b\), and reference baseline \(b_0\) (typically `default`):
\[
\Delta M(b\mid b_0) = M_b - M_{b_0}
\]
Sign interpretation:

- \( \Delta \mathrm{UER} > 0 \): worse safety.
- \( \Delta \mathrm{FAR} > 0 \): worse diagnosability.
- \( \Delta \mathrm{TCR} > 0 \): better trace coverage.
- \( \Delta \mathrm{EDS} > 0 \): better error determinism.

## 7. Multi-Seed Stability (Mean and Std)
For metric \(M\) across seeds \(s \in \mathcal{S}\):
\[
\mu_M(b) = \frac{1}{S}\sum_{s=1}^{S} M_{b,s}
\]
\[
\sigma_M(b) = \sqrt{\frac{1}{S}\sum_{s=1}^{S}\left(M_{b,s}-\mu_M(b)\right)^2}
\]
Reported as \( \mu \pm \sigma \). Smaller \( \sigma \) indicates higher run-to-run stability.
