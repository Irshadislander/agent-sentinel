# Appendix: Statistical Reporting Protocol

This appendix defines how confidence intervals, deltas, and aggregate summaries are produced.

## 1) Confidence Intervals

Primary uncertainty reporting uses 95% confidence intervals.

- Recommended method: non-parametric bootstrap.
- Resampling unit: per-run metric values within a fixed slice.
- Slice key: `(system, attack_family, difficulty)`.
- CI type: percentile interval.
- CI level: 95%.

If a different CI method is used, it must be explicitly labeled in the table caption.

## 2) Delta vs Baseline / Reference

For metric \(m\), delta for system \(s\) versus reference \(s_0\):

\[
\Delta m(s,f,d)=m(s,f,d)-m(s_0,f,d)
\]

Reference conventions:
- baseline comparison tables: \(s_0=\) `default`
- ablation comparison tables: \(s_0=\) `full_system`

Each section must state the reference explicitly.

## 3) What Is Averaged

- First compute per-run metric values for each `(system, family, difficulty)` slice.
- Reported mean is the average over repeated runs/seeds for that slice.
- Aggregates may be:
  - macro average (equal weight by slice), or
  - micro average (weight by task/request count),
  and must be labeled as macro or micro.

## 4) Required Reporting Slices

Primary metrics should be reported at:

1. system-level aggregate,
2. attack-family summary,
3. difficulty summary,
4. system x family x difficulty slices (full matrix in artifacts; condensed in paper).

## 5) Table Output Contract

For each primary metric table row, include where available:
- point estimate (mean),
- 95% CI,
- delta vs reference,
- sample size indicator (`n` runs and/or tasks).

No synthetic values should be inserted. Unavailable slices stay as placeholders.

## 6) Reproducibility

- Use deterministic aggregation scripts and fixed seeds where supported.
- Keep artifact source path and generation timestamp in table headers.
- Ensure `results_tables.md` and `STATS_TABLES.md` are generated from the same artifact snapshot.

## 7) Example Aggregation Command

```bash
python3 scripts/aggregate_results.py \
  --input artifacts/bench \
  --out paper/results_tables.md \
  --stats-out paper/STATS_TABLES.md \
  --baseline default \
  --resamples 10000
```

Expected outputs:
- `paper/results_tables.md`
- `paper/STATS_TABLES.md`
