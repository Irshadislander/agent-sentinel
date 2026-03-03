# Day 11 Results Summary

## Key Findings

- UER shift (no_policy - default): +0.7342
- TCR shift (no_trace - default): -0.8741
- FAR shift (raw_errors - default): +1.0000

## Bullet Insights

- Policy bypass remains the dominant unsafe-execution failure mode in this harness.
- Trace suppression is immediately visible in completeness metrics and forensic utility.
- Raw exception paths materially increase ambiguity relative to structured error mapping.
- Sensitivity sweeps should be interpreted jointly with latency percentiles, not in isolation.
