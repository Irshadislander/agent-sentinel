# Paper Artifacts

This directory contains research artifacts used for the formal write-up and evaluation framing.

- `NICHE.md`: precise problem niche, scope, and non-goals.
- `FORMAL_MODEL.md`: formal capability execution model, notation, definitions, and guarantees.
- `METRICS.md`: security/evaluation metric definitions and experimental protocol.
- `EVAL_PROTOCOL.md`: baseline definitions, experimental procedure, and reproducibility protocol.
- `NOVELTY.md`: falsifiable novelty statement, gap analysis, and disproof criteria.
- `CLAIMS.md`: hypothesis set (H1-H4) with metric-level expected effects.
- `EXPERIMENTS.md`: setup, reporting protocol, and statistical plan.
- `THREAT_MODEL.md`: adversary, assumptions, guarantees, and failure modes.
- `ROBUSTNESS.md`: attack scenario mapping and expected denial/trace signatures.
- `RELATED_WORK.md`: literature buckets and positioning map.
- `results_tables.md`: generated markdown result tables from matrix outputs.

Day 1-2 goal: formal model + metrics definitions.

## Paper Map

- [NICHE](NICHE.md)
- [NOVELTY](NOVELTY.md)
- [CLAIMS](CLAIMS.md)

## Elevator Pitch

Agent Sentinel studies runtime control for tool-using agents at the capability boundary, where unsafe execution and ambiguous failure are most operationally costly.  
The method combines policy gating, plugin isolation, structured errors, and trace completeness with explicit ablation baselines.  
Claims are evaluated through adversarial tasks and matrix benchmarks using UER, FAR, TCR, EDS, and latency statistics.  
The contribution is not a new model, but a falsifiable enforcement-and-measurement framework that supports reproducible safety-observability tradeoff analysis.  
All tables and reports are generated from scripted outputs to keep implementation behavior aligned with paper claims.

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
