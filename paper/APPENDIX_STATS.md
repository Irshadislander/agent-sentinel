# Appendix: Statistical Rigor

## Confidence Interval Method
We use non-parametric bootstrap confidence intervals (95%) for metric means and latency percentiles.

### Bootstrap Configuration
- Resampling unit: per-run metric values within each baseline/scenario group.
- Resamples: **10,000** by default.
- CI type: percentile interval with \(\alpha = 0.05\).
- Determinism: fixed RNG seed in the aggregation script for reproducible intervals.

## Effect Size Definition
For each ablation \(a\) and metric \(m\), the reported effect is:
\[
\Delta m_a = \hat{m}_a - \hat{m}_{\text{baseline}}
\]
where \(\hat{m}\) is the sample mean for that metric.

For latency, we also report:
- \(\Delta\) mean latency (ms) with bootstrap 95% CI.
- Cohen's \(d\) against the baseline latency distribution.

## Baseline Definition
- Primary baseline: `default` (full system).
- If `default` is missing, the first deterministic baseline in sorted order is used.
- The effective baseline used for each run is written into generated tables.

## Assumptions and Limits
- Samples are treated as exchangeable within each baseline/scenario slice.
- Bootstrap intervals are descriptive uncertainty estimates, not formal hypothesis-test p-values.
- Small-\(n\) groups are retained; intervals remain valid but wider.

## Reproduction Command
```bash
python3 scripts/aggregate_results.py \
  --input artifacts/bench \
  --out paper/results_tables.md \
  --stats-out paper/STATS_TABLES.md \
  --baseline default \
  --resamples 10000
```

Outputs:
- `paper/results_tables.md`
- `paper/STATS_TABLES.md`
