# Appendix: Statistical Rigor

## Confidence Intervals
We report bootstrap 95% confidence intervals for key metrics (latency p50/p95/p99, attack success rate, trace completeness).

## Effect Sizes
For each ablation we report delta relative to baseline:
\[
\Delta = \hat{m}_{abl} - \hat{m}_{base}
\]
and a 95% CI on Δ via bootstrap.

## Notes
We avoid p-value spam. Significance tests are only used where appropriate and effect sizes are emphasized.

## Generated statistical tables
Run:

```bash
python3 scripts/aggregate_results.py
```

Outputs:
- `paper/results_tables.md` (CI-augmented summary table)
- `paper/STATS_TABLES.md` (delta/effect-size and percentile-CI tables)
