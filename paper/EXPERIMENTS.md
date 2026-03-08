# Experiments

## Evaluation Objective
We evaluate whether deterministic runtime capability mediation improves security outcomes for tool-using agents while preserving acceptable runtime cost and decision observability.

Primary security outcomes:
- **Attack Success Rate (ASR)**,
- **Attack Block Rate (ABR)**.

## Systems and Conditions
### Reference
- `full_system`

### Baselines
- `no_enforcement`
- `allow_all`
- `naive_allow_list`
- `llm_guard_style` (optional/future, reported as `NA` if unavailable)

### Ablations
- `no_default_deny`
- `no_first_match_ordering`
- `no_trace` / `reduced_observability`
- `no_capability_confinement`
- `no_enforcement`

## Benchmark Design
The benchmark matrix is:

\[
\text{attack family} \times \text{difficulty level} \times \text{baseline/ablation} \times \text{metric}
\]

Attack families:
- `prompt_injection`
- `filesystem_damage`
- `shell_misuse`
- `data_exfiltration`
- `network_exfiltration`

Difficulty levels:
- `easy`
- `medium`
- `hard` / `multi_step`

## Reporting Artifacts (Tables and Figures)
Paper-facing tables are generated from benchmark outputs and organized in `paper/tables/` (for example `table_baselines.md`, `table_asr.md`, `table_results_day12.md`, `table_appendix_day12.md`).

Paper-facing figures are generated in `paper/figures/` (for example architecture overview, baseline comparison, trace tradeoff, and latency tradeoff figures).

Supporting benchmark outputs are stored in `artifacts/bench/` (for example `matrix.json`, policy performance JSON, and robustness JSON).

## Real Agent Evaluation
We include a minimal real-agent integration case study in `examples/agent_integration/run_case_study.py`. The harness simulates a tool-using agent loop in which prompt-derived requests are routed through `ToolGateway`, mediated by policy/capability checks, and resolved as `allow` or `deny` with trace output.

Case-study scenarios include:
- benign safe-action requests under restrictive policy,
- shell-misuse attack attempts,
- permissive-policy control behavior.

This is a runtime mediation demonstration and integration check, not a claim of large-scale production deployment.

## Execution and Reproducibility
1. Run benchmark slices across systems/ablations.
2. Collect decision, latency, and trace artifacts.
3. Aggregate into matrix outputs.
4. Render paper-facing tables and figures from generated artifacts.

Statistical reporting uses consistent workload slices and confidence intervals; no manual result synthesis is used in paper tables.
