# Core Claims

## Contributions (C1-C5)

### C1: Formal runtime capability-gating semantics
We formalize runtime enforcement as a capability-level decision function with explicit allow/deny outcomes, exit-code classes, and trace emission expectations. This is measurable through deterministic decision-class and exit-class consistency across repeated runs.

### C2: Ablation framework over safety/observability/extensibility axes
We define controlled baseline removals (`no_policy`, `no_trace`, `raw_errors`, `no_plugin_isolation`) that isolate which control layer drives each metric change. This is measurable by baseline deltas over UER, FAR, TCR, EDS, and latency distributions.

### C3: Adversarial task suite for observable baseline deltas
We provide adversarial tasks (policy-blocked, malformed payload, plugin violation, trace-required) that force distinct failure and enforcement paths. This is measurable by non-zero baseline separation where expected (for example UER in `no_policy`, TCR drop in `no_trace`).

### C4: Reproducible evaluation pipeline with artifacts
We connect runner scripts, matrix outputs, and CI artifact publication into a repeatable workflow for paper tables and figure generation. This is measurable by regenerating the same report schema from fixed inputs without manual edits.

### C5: Built-in tradeoff analysis hooks
We expose latency percentiles, trace completeness, plugin isolation signals, and multi-seed aggregation hooks to study safety-performance tradeoffs. This is measurable through per-baseline p50/p95 latency and completeness metrics reported in matrix outputs.

## Core Hypotheses

### H1: Policy gating drives unsafe execution toward zero
- Metric: Unsafe Execution Rate (UER)
- Formal statement: \( \mathrm{UER}_{\text{default}} < \mathrm{UER}_{\text{no\_policy}} \), with target \( \mathrm{UER}_{\text{default}} = 0 \).
- Expected direction: decrease (\(\downarrow\))
- Baseline comparison: `default` vs `no_policy`

### H2: Structured errors reduce failure ambiguity
- Metric: Failure Ambiguity Rate (FAR)
- Formal statement: \( \mathrm{FAR}_{\text{default}} < \mathrm{FAR}_{\text{raw\_errors}} \).
- Expected direction: decrease (\(\downarrow\))
- Baseline comparison: `default` vs `raw_errors`

### H3: Trace enforcement ensures complete request tracing
- Metric: Trace Completeness Ratio (TCR)
- Formal statement: \( \mathrm{TCR}_{\text{default}} > \mathrm{TCR}_{\text{no\_trace}} \), with target \( \mathrm{TCR}_{\text{default}} = 1 \).
- Expected direction: increase (\(\uparrow\))
- Baseline comparison: `default` vs `no_trace`

### H4: Deterministic exit taxonomy improves consistency
- Metric: Exit Determinism Score (EDS)
- Formal statement: \( \mathrm{EDS}_{\text{default}} > \mathrm{EDS}_{\text{raw\_errors}} \).
- Expected direction: increase (\(\uparrow\))
- Baseline comparison: `default` vs `raw_errors`

These hypotheses operationalize the novelty claims introduced in Section X of the formal model.
