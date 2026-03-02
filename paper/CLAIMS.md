# Core Claims

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
