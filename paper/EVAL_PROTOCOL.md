# Evaluation Protocol

## Objective
Evaluate Agent-Sentinel as a benchmarked runtime security system under structured adversarial workloads. The protocol is baseline-oriented and reports security effectiveness, latency overhead, and decision-trace quality.

## Benchmark Matrix
Primary evaluation matrix:

\[
\text{attack family} \times \text{difficulty level} \times \text{baseline} \times \text{metric}
\]

This matrix is the canonical structure for all reported comparisons.

## Attack Families
- `prompt_injection`
- `filesystem_damage`
- `shell_misuse`
- `data_exfiltration`
- `network_exfiltration`

Family definitions and scenario examples are specified in [ATTACK_SCENARIOS](ATTACK_SCENARIOS.md).

## Difficulty Levels
- `easy`: direct single-step unsafe attempt.
- `medium`: partially obfuscated or indirect unsafe attempt.
- `hard` / `multi_step`: chained sequence with staged escalation.

## Baseline Systems
Reference: `full_system`.

Compared baselines:
- `no_enforcement`
- `allow_all`
- `naive_allow_list`
- `llm_guard_style` (optional/future unless implemented)

If a baseline is unimplemented in the current runner, keep its row and report `NA`.

## Evaluation Pipeline
1. Load workloads from `configs/tasks/` and `configs/tasks_synth/`.
2. Assign each case to an attack family and difficulty level.
3. Execute each `(family, difficulty)` slice for each baseline.
4. Apply runtime policy enforcement and collect decision artifacts.
5. Compute metrics per matrix cell.
6. Aggregate into benchmark tables and statistical summaries.

## Reporting Views
- Overall baseline comparison.
- Attack Family Summary.
- Difficulty-Level Summary.
- Family × Difficulty Comparison.
- Per-Family Baseline Comparison.

## Metrics
Primary metrics are defined in [METRICS](METRICS.md):
- attack block rate,
- attack success rate,
- latency overhead,
- trace completeness,
- decision artifact / explainability coverage.

## Repetition and Statistics
- Use repeated runs when available.
- Report mean and confidence intervals.
- Preserve deterministic artifact generation and run metadata.
