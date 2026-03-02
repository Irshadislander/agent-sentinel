# Paper Artifacts

This directory contains research artifacts used for the formal write-up and evaluation framing.

- `FORMAL_MODEL.md`: formal capability execution model, notation, definitions, and guarantees.
- `METRICS.md`: security/evaluation metric definitions and experimental protocol.
- `EVAL_PROTOCOL.md`: baseline definitions, experimental procedure, and reproducibility protocol.
- `CLAIMS.md`: hypothesis set (H1-H4) with metric-level expected effects.
- `EXPERIMENTS.md`: setup, reporting protocol, and statistical plan.
- `results_tables.md`: generated markdown result tables from matrix outputs.

Day 1-2 goal: formal model + metrics definitions.

## Reproduce Results

```bash
make bench
python -m agent_sentinel.benchmark.run_benchmark --matrix --matrix-all-baselines
python scripts/generate_paper_tables.py
```
