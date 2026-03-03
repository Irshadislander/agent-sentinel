# Day 12 Results Summary

## Key Findings

## Seed Stability (mean ± std)

- scale_n200 / default: UER=0.0000±0.0000, FAR=0.0000±0.0000, TCR=1.0000±0.0000, EDS=1.0000±0.0000
- scale_n200 / no_plugin_isolation: UER=0.0000±0.0000, FAR=0.0000±0.0000, TCR=1.0000±0.0000, EDS=1.0000±0.0000
- scale_n200 / no_policy: UER=1.0000±0.0000, FAR=0.0000±0.0000, TCR=1.0000±0.0000, EDS=1.0000±0.0000
- scale_n200 / no_trace: UER=0.0000±0.0000, FAR=0.0000±0.0000, TCR=0.0000±0.0000, EDS=1.0000±0.0000
- scale_n200 / raw_errors: UER=0.0000±0.0000, FAR=1.0000±0.0000, TCR=1.0000±0.0000, EDS=1.0000±0.0000

## Bullet Insights

- Policy bypass drives the largest unsafe-execution increase in this harness.
- Trace suppression directly reduces forensic completeness.
- Raw exception pathways increase ambiguity relative to structured errors.
- Seed-level aggregation is required for stable comparison claims.
