# Evaluation

## Setup
The evaluation uses fixed tasks plus adversarial scenarios under baseline and ablation modes. Runs are automated and artifact-backed for reproducibility.

## Metrics
Primary metrics include safety (UER), failure disambiguation (FAR), trace completeness (TCR), determinism/explainability scores, and latency percentiles (p50/p95/p99).

## Protocol
We execute matrix runs over baseline modes and scenario classes, then aggregate results into canonical tables and appendix-level reports.

## Outputs
- Main comparison tables in `results_tables.md`.
- Robustness-specific analysis in `ROBUSTNESS.md`.
- Performance summaries and latency distributions in `PERF_DAYXX.md`.

## Links
- [FORMAL_MODEL](FORMAL_MODEL.md)
- [THREAT_MODEL](THREAT_MODEL.md)
- [METRICS](METRICS.md)
- [RESULTS](results_tables.md)
- [ROBUSTNESS](ROBUSTNESS.md)
- [PERF](PERF_DAYXX.md)
