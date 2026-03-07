# Experiments

## 1. What Is Evaluated
We evaluate whether deterministic runtime capability gating improves security and observability for tool-augmented agents under adversarial workloads, and what latency overhead this introduces.

## 2. Systems and Baselines
### Reference mode
- `full_system`: Agent-Sentinel with deterministic policy evaluation, capability checks, default-deny behavior, and structured trace output.

### Baseline conditions
- `no_enforcement`: direct tool execution without runtime gating.
- `allow_all`: permissive policy condition.
- `naive_allow_list`: coarse allow-list condition.
- `llm_guard_style`: optional/future baseline unless explicitly implemented.

### Ablation conditions
- `no_default_deny`
- `no_first_match_ordering`
- `no_trace` / `reduced_observability`
- `no_capability_confinement` / `coarse_capability_gating`
- `no_enforcement`

Baselines establish comparative security posture; ablations isolate causal effect of removed controls.

## 3. Attack Families and Difficulty
### Attack families
- `prompt_injection`
- `filesystem_damage`
- `shell_misuse`
- `data_exfiltration`
- `network_exfiltration`

### Difficulty levels
- `easy`
- `medium`
- `hard` / `multi_step`

## 4. Baseline Comparison Matrix
\[
\text{baseline} \times \text{attack family} \times \text{difficulty level} \times \text{metric}
\]

where baseline includes `full_system`, `no_enforcement`, `allow_all`, `naive_allow_list`, and optional `llm_guard_style` when available.

## 5. Full Experiment Matrix
\[
\text{system mode} \times \text{attack family} \times \text{difficulty level} \times \text{metric}
\]

This matrix covers baseline and ablation reporting with identical workload slices.

## 6. Evaluation Workflow
1. Load workloads from `configs/tasks/` and `configs/tasks_synth/`.
2. Execute each slice under selected system mode.
3. Apply runtime policy enforcement at the tool decision boundary.
4. Record decisions, latency, and decision artifacts.
5. Compute metrics by mode, family, and difficulty.
6. Export artifacts and paper tables.

## 7. Metrics Reported
Primary metrics (defined in [METRICS](METRICS.md)):
- attack block rate,
- attack success rate,
- latency overhead,
- trace completeness,
- structured decision artifact coverage.

Reporting views:
- overall baseline comparison,
- baseline by family,
- baseline by difficulty,
- overhead comparison,
- deltas versus `full_system`.

## 8. Runtime Environment Reporting
For each run set, record:
- CPU model and core count,
- RAM,
- OS/kernel string,
- Python version,
- git commit SHA.

Runtime assumptions:
- Python 3.11+,
- development install via `pip install -e ".[dev]"`.

## 9. Repetition and Statistical Summary
- Run repeated trials when available.
- Report mean and spread (standard deviation and/or confidence intervals).
- Preserve run metadata and artifacts for reproducibility.
