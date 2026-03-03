# Novelty

## Falsifiable Novelty Claim

This work contributes a runtime capability-governance framework whose policy gating, structured errors, plugin isolation, and trace completeness produce measurable and reproducible safety-observability deltas against ablated baselines on adversarial tasks.

## What Prior Work Lacks

- Runtime safety controls are often described qualitatively, without a deterministic decision taxonomy tied to explicit exit semantics.
- Reported evaluations frequently omit controlled ablation baselines (`no_policy`, `no_trace`, `raw_errors`, `no_plugin_isolation`) needed for causal attribution.
- Failure handling is commonly untyped or ad hoc, reducing error disambiguation and limiting reproducible auditability across runs.

## What We Provide

- A capability registry and policy gating boundary with explicit allow/deny semantics and non-bypassable execution ordering.
- A baseline-aware matrix benchmark with adversarial tasks and metrics (UER, FAR, TCR, EDS, plus latency/trace/plugin hooks) for falsifiable comparisons.
- A reproducible pipeline (scripts + CI artifacts + paper tables) that keeps implementation outputs aligned with evaluation claims.

## What Would Disprove Us

- If default mode fails to outperform at least one expected baseline direction (e.g., UER vs `no_policy`, TCR vs `no_trace`, FAR/EDS vs `raw_errors`) on controlled tasks.
- If repeated runs under fixed seeds and fixed configuration cannot reproduce stable metric trends within reported multi-seed variability bounds.
