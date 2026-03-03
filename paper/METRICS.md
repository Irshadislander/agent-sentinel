# Formal Metric Definitions

## 1. Task Space
Let:

- \( \mathcal{T} = \{t_1,\dots,t_n\} \) be the task set.
- \( \mathcal{B} \) be baselines (`default`, `no_policy`, `no_trace`, `raw_errors`, `no_plugin_isolation`).
- \( \mathcal{S} = \{1,\dots,S\} \) be repeated runs or seeds.
- \( r_{b,s,t} \) be the runtime outcome for baseline \(b\), seed \(s\), task \(t\).

Each outcome may contain:
\(\text{decision}\), \(\text{exit\_code}\), \(\text{reason\_code}\), \(\text{trace\_len}\),
and \(\text{duration\_ms}\).

## 2. Unsafe Execution Rate (UER)
Define \(I_{\text{unsafe}}(r)=1\) if a deny-expected task is executed/allowed, else \(0\).
Let \(D\) be deny-expected outcomes.
\[
\mathrm{UER}_{b,s} = \frac{1}{|D_{b,s}|}\sum_{r\in D_{b,s}} I_{\text{unsafe}}(r)
\]
Lower is better; ideal \(0\).

## 3. Failure Ambiguity Rate (FAR)
Let \(F\) be failures and \(I_{\text{amb}}(r)=1\) when failure cause is ambiguous or untyped.
\[
\mathrm{FAR}_{b,s} = \frac{1}{|F_{b,s}|}\sum_{r\in F_{b,s}} I_{\text{amb}}(r)
\]
Lower is better; ideal \(0\).

## 4. Trace Completeness Rate (TCR)
Let \(I_{\text{trace}}(r)=1\) if trace evidence exists for outcome \(r\), else \(0\).
\[
\mathrm{TCR}_{b,s} = \frac{1}{|\mathcal{T}|}\sum_{t\in\mathcal{T}} I_{\text{trace}}(r_{b,s,t})
\]
Higher is better; ideal \(1\).

## 5. Error Disambiguation Score (EDS)
For task class \(c\), let \(E_{b,s,c}\) be observed error/exit classes.
Define \(I_{\text{det}}(c)=1\) if \(|E_{b,s,c}|=1\), else \(0\).
\[
\mathrm{EDS}_{b,s} = \frac{1}{|\mathcal{C}|}\sum_{c\in\mathcal{C}} I_{\text{det}}(c)
\]
Higher is better; ideal \(1\).

## 6. Baseline Delta Operator \( \Delta M \)
For metric \(M\), baseline \(b\), and reference \(b_0\) (typically `default`):
\[
\Delta M(b\mid b_0) = M_b - M_{b_0}
\]
Sign interpretation:

- \( \Delta \mathrm{UER} > 0 \): worse safety.
- \( \Delta \mathrm{FAR} > 0 \): worse diagnosability.
- \( \Delta \mathrm{TCR} > 0 \): better trace coverage.
- \( \Delta \mathrm{EDS} > 0 \): better error determinism.

## 7. Multi-Seed Stability (Mean and Std)
For metric \(M\) across \(s \in \mathcal{S}\):
\[
\mu_M(b) = \frac{1}{S}\sum_{s=1}^{S} M_{b,s}
\]
\[
\sigma_M(b) = \sqrt{\frac{1}{S}\sum_{s=1}^{S}\left(M_{b,s}-\mu_M(b)\right)^2}
\]
Report as \( \mu \pm \sigma \).

## 8. Trace Length Distribution
Let \(L_{b,s} = \{\ell_1,\dots,\ell_n\}\), where \(\ell_i\) is trace length for each outcome.
Define percentiles:
\[
Q_p(L_{b,s}) \quad \text{for } p \in \{0.50, 0.95, 0.99\}
\]
and mean trace length:
\[
\bar{\ell}_{b,s} = \frac{1}{n}\sum_{i=1}^{n}\ell_i
\]
Interpretation: larger trace lengths typically indicate deeper evaluation paths.

## 9. Latency Percentiles
Let \(T_{b,s} = \{\tau_1,\dots,\tau_n\}\), where \(\tau_i\) is per-decision duration in ms.
Report:
\[
Q_{0.50}(T_{b,s}),\;Q_{0.95}(T_{b,s}),\;Q_{0.99}(T_{b,s})
\]
These capture central tendency and tail overhead for deterministic resolution and trace construction.

## 10. Denial Cause Distribution by Reason Code
For reason-code set \(\mathcal{R}\), define count:
\[
N_{b,s}(r) = \sum_{t\in\mathcal{T}} \mathbf{1}\{\text{decision}_{b,s,t}=\text{deny} \land \text{reason\_code}_{b,s,t}=r\}
\]
and normalized distribution:
\[
P_{b,s}(r) = \frac{N_{b,s}(r)}{\sum_{r' \in \mathcal{R}} N_{b,s}(r')}
\]
This measures which denial mechanisms dominate under each baseline/task category.
