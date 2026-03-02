# Paper Artifacts

This directory contains research artifacts used for the formal write-up and evaluation framing.

- `FORMAL_MODEL.md`: formal capability execution model, notation, definitions, and guarantees.
- `METRICS.md`: security/evaluation metric definitions and experimental protocol.
- `EVAL_PROTOCOL.md`: baseline definitions, experimental procedure, and reproducibility protocol.
- `CLAIMS.md`: hypothesis set (H1-H4) with metric-level expected effects.
- `EXPERIMENTS.md`: setup, reporting protocol, and statistical plan.
- `NOVELTY.md`: concise novelty claims and contribution framing.
- `THREAT_MODEL.md`: adversary, assumptions, guarantees, and failure modes.
- `RELATED_WORK.md`: literature buckets and positioning map.
- `results_tables.md`: generated markdown result tables from matrix outputs.

Day 1-2 goal: formal model + metrics definitions.

## Paper Skeleton Order

1. `FORMAL_MODEL.md`
2. `THREAT_MODEL.md`
3. `RELATED_WORK.md`
4. `NOVELTY.md`
5. `METRICS.md`
6. `CLAIMS.md`
7. `EVAL_PROTOCOL.md`
8. `EXPERIMENTS.md`
9. `results_tables.md` (generated)

## Reproduce Results

```bash
./scripts/reproduce_paper_results.sh
```
