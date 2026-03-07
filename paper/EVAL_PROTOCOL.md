# Evaluation Protocol

## Objective
Evaluate Agent-Sentinel as a benchmarked runtime security system, not only as a demo.
The protocol measures attack blocking, runtime overhead, and quality of decision artifacts under adversarial workloads.

## Adversarial Workload Taxonomy
Tasks are grouped into five attack families:

1. `prompt_injection`: attacker attempts to override policy through instructions.
2. `filesystem_damage`: destructive or unauthorized file modification/deletion.
3. `shell_misuse`: unsafe command execution attempts.
4. `data_exfiltration`: attempts to read and extract sensitive local data.
5. `network_exfiltration`: attempts to send sensitive data to external endpoints.

Each task has an expected policy outcome (`allow` or `deny`) for correctness and block-rate measurement.

## Difficulty Levels
Adversarial tasks are labeled by difficulty:

1. `easy`: direct single-step unsafe request.
2. `medium`: partial obfuscation or indirect unsafe intent.
3. `hard` / `multi_step`: chained sequence where benign steps lead to unsafe execution/exfiltration.

## Baseline Systems (Evaluation Modes)
We compare `default` (full Agent-Sentinel) against baseline conditions.
If a baseline is not implemented in the current runner, it is explicitly treated as planned/optional.

1. **No enforcement** (`no_policy` / `no_gateway_enforcement` mode).
   Shows expected attack behavior when runtime gating is absent.
2. **Allow-all** (permissive policy condition).
   Isolates the effect of policy strictness from gateway mechanics.
3. **Naive allow-list** (simplified capability allow-list condition).
   Tests whether basic allow-listing is sufficient without richer checks/artifacts.
4. **Optional LLM-guard style baseline** (future/optional condition).
   Compares probabilistic prompt-side filtering with deterministic runtime gating.

## Step-by-Step Evaluation Pipeline
1. **Workload generation**
   - Load tasks from `configs/tasks/` and synthetic workloads from `configs/tasks_synth/`.
   - Attach attack-family and difficulty labels.
2. **Attack injection / execution**
   - Execute each adversarial task prompt/request under the selected system mode.
3. **Policy enforcement**
   - Resolve runtime allow/deny decisions at the enforcement boundary.
4. **Trace logging**
   - Emit structured decision artifacts and trace metadata (`decision`, `rule_id`, `reason_code`, trace fields).
5. **Metric computation**
   - Compute ABR, ASR, latency overhead, trace completeness, and decision-artifact coverage.
6. **Aggregation and reporting**
   - Aggregate by system/family/difficulty and generate paper-facing result tables.

## Ablation Study Methodology
To isolate why each control matters, we evaluate targeted ablations that remove or weaken one component at a time.
Each mode is treated as an explicit evaluation condition (implemented or planned).

| Ablation mode | Component removed/weakened | Expected degradation / failure mode | Metrics most affected |
|---|---|---|---|
| `full_system` | none (reference mode) | strongest blocking and audit quality | all metrics (reference) |
| `no_default_deny` | deny fallback for unmatched/invalid paths removed/weakened | unsafe fallthrough on unmatched requests | attack block rate, safety correctness |
| `no_first_match_ordering` | deterministic first-match rule resolution removed | unstable/conflicting decisions under overlapping rules | attack block rate, decision consistency, explainability clarity |
| `no_trace` / `reduced_observability` | trace emission reduced/disabled | forensic visibility loss and weaker explanations | trace completeness, structured artifact coverage |
| `no_capability_confinement` / `coarse_capability_gating` | fine-grained capability boundary weakened | privilege overreach, cross-capability leakage | attack block rate, unsafe execution indicators |
| `no_enforcement` | runtime enforcement bypassed | highest attack success / no authorization boundary | attack block rate (largest drop), safety correctness |

This ablation suite is intended to show:
- why default-deny matters,
- why deterministic ordering matters,
- why tracing matters,
- why capability confinement matters.

## Experiment Matrix
Primary matrix:

\[
\text{ablation modes} \times \text{attack families} \times \text{difficulty levels} \times \text{metrics}
\]

Reporting views:
- aggregate by ablation mode,
- breakdown by family,
- breakdown by family x difficulty,
- deltas against `full_system`.

## Metrics
Primary metrics are defined in [METRICS](METRICS.md):
- attack block rate,
- latency overhead,
- trace completeness,
- structured decision artifact coverage.

## Repetitions and Aggregation
- Repeat runs across seeds/repetitions (minimum 10 when available).
- Report mean and spread (std and/or confidence intervals when available).
- Generate tables deterministically from artifact JSON.
