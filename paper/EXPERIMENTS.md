# Experiments

## 1. What Is Evaluated
We evaluate whether deterministic runtime capability gating improves security and observability for tool-augmented agents under adversarial workloads, and what latency overhead this enforcement introduces.

## 2. Systems and Baselines
### Reference mode
- `full_system`: Agent-Sentinel with deterministic policy evaluation, capability checks, and structured trace output.

### Baseline conditions
- `no_enforcement`: direct tool execution without runtime gating.
- `allow_all`: permissive policy condition.
- `naive_allow_list`: coarse allow-list style condition.
- optional `llm_guard_style` baseline if implemented; otherwise reported as planned.

### Ablation conditions
- `no_default_deny`
- `no_first_match_ordering`
- `no_trace` / `reduced_observability`
- `no_capability_confinement` / `coarse_capability_gating`
- `no_enforcement`

Baselines characterize comparative security posture; ablations isolate the effect of removing specific controls.

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

## 4. Experiment Matrix
\[
\text{system mode} \times \text{attack family} \times \text{difficulty} \times \text{metrics}
\]

This matrix is used consistently for reference, baseline, and ablation comparisons.

## 5. Evaluation Workflow
1. Load workloads from `configs/tasks/` and `configs/tasks_synth/`.
2. Execute each workload slice under the selected system mode.
3. Apply runtime policy enforcement at the tool decision boundary.
4. Record allow/deny decisions, latency, and decision artifacts.
5. Compute metrics by system, family, and difficulty.
6. Export artifacts and reporting tables.

## 6. Metrics Reported
Primary metrics (defined in [METRICS](METRICS.md)):
- attack block rate,
- attack success rate,
- latency overhead,
- trace completeness,
- structured decision artifact coverage.

Reporting includes overall aggregates, per-family views, per-family x difficulty views, and deltas versus reference mode.

## 7. Runtime Environment Reporting
For each run set, record:
- CPU model and core count,
- RAM,
- OS/kernel string,
- Python version,
- git commit SHA.

Runtime assumptions:
- Python 3.11+,
- development install via `pip install -e ".[dev]"`.

## 8. Repetition and Statistical Summary
- Run repeated trials when available.
- Report mean and spread (standard deviation and/or confidence intervals per stats protocol).
- Preserve run metadata and artifacts to keep comparisons reproducible.
