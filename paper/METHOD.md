# Method

## Enforcement Points

The runtime enforces safety and reliability at three explicit boundaries:

1. **Policy gate before execution**
   - Capability/tool requests are evaluated before any tool call executes.
   - Denials stop execution and propagate deterministic deny outcomes.

2. **Structured error boundary**
   - Runtime failures are mapped to structured error kinds and stable exit classes.
   - This reduces ambiguity in downstream analysis and metric computation.

3. **Trace emission boundary**
   - Request outcomes emit structured events for auditability and reproducibility.
   - Trace completeness is measured directly (TCR) rather than assumed.

## Baseline Toggles as Controlled Removals

Each baseline removes one control layer while holding task set and runner constant:

- `no_policy`: bypasses enforcement gate (expected UER increase).
- `no_trace`: disables trace writes (expected TCR decrease).
- `raw_errors`: uses unstructured exception strings (expected FAR increase).
- `no_plugin_isolation`: disables plugin isolation checks (expected plugin surface increase).

This design supports causal interpretation by attributing metric changes to specific control removals.

## Why Adversarial Tasks Are Required

Benign-only workloads can mask safety failures by producing similar aggregate success across baselines. Adversarial tasks intentionally exercise denied actions, malformed payloads, plugin-contract violations, and trace-sensitive paths so that differences in UER, FAR, TCR, and plugin-load behavior become observable and statistically reportable.
