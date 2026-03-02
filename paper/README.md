# Paper Artifacts

This directory contains research artifacts used for the formal write-up and evaluation framing.

- `FORMAL_MODEL.md`: formal capability execution model, notation, definitions, and guarantees.
- `ABSTRACT.md`: concise problem-method-evaluation summary.
- `INTRODUCTION.md`: motivation, gap statement, and contributions.
- `PROBLEM.md`: entities, trust boundary, and formal objective.
- `METHOD.md`: enforcement mechanism and controlled baseline removals.
- `METRICS.md`: security/evaluation metric definitions and experimental protocol.
- `EVAL_PROTOCOL.md`: baseline definitions, experimental procedure, and reproducibility protocol.
- `CLAIMS.md`: hypothesis set (H1-H4) with metric-level expected effects.
- `EXPERIMENTS.md`: setup, reporting protocol, and statistical plan.
- `NOVELTY.md`: concise novelty claims and contribution framing.
- `THREAT_MODEL.md`: adversary, assumptions, guarantees, and failure modes.
- `RELATED_WORK.md`: literature buckets and positioning map.
- `results_tables.md`: generated markdown result tables from matrix outputs.
- `CONCLUSION.md`: placeholder for final discussion and limitations.
- `FIG_SYSTEM.txt`: ASCII system pipeline sketch.
- `FIG_THREATMODEL.txt`: ASCII threat/defense sketch.

Day 1-2 goal: formal model + metrics definitions.

## Paper Skeleton Order

1. `ABSTRACT.md`
2. `INTRODUCTION.md`
3. `PROBLEM.md`
4. `METHOD.md`
5. `METRICS.md`
6. `EVAL_PROTOCOL.md`
7. `EXPERIMENTS.md`
8. `results_tables.md` (generated)
9. `THREAT_MODEL.md`
10. `RELATED_WORK.md`
11. `CONCLUSION.md` (placeholder)

## Reproduce Results

```bash
./scripts/reproduce_paper_results.sh
```
