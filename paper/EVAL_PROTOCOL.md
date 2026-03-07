# Evaluation Protocol

## Objective
Evaluate Agent-Sentinel as a runtime security system using explicit baseline comparisons under adversarial workloads. The protocol measures security effectiveness, runtime overhead, and decision-trace quality.

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

## Baseline Systems
Reference system: `full_system` (Agent-Sentinel with deterministic runtime capability gating, ordered rule resolution, default deny, and structured decision artifacts).

If a baseline mode is unavailable in a given runner, report it as planned/optional and keep table entries as `NA`.

| Baseline | What it allows | What it blocks | Why included | What comparison it enables |
|---|---|---|---|---|
| **No Enforcement** (`no_enforcement` / `no_policy`) | tool requests proceed without runtime gate | only downstream/tool-native failures | lower-bound condition without authorization boundary | effect of adding runtime enforcement |
| **Allow-All Policy** (`allow_all`) | all capabilities by policy | almost nothing at policy layer | isolates policy strictness from gateway mechanics | permissive policy vs least-privilege policy |
| **Naive Allow-List** (`naive_allow_list`) | requests matching coarse allow-list entries | requests outside the allow-list | tests whether coarse filtering is sufficient | naive allow-list vs capability-aware deterministic gating |
| **LLM-Guard Style Baseline** (`llm_guard_style`) | requests accepted by probabilistic prompt-side filter | prompt patterns judged unsafe by the filter | contrasts probabilistic filtering with deterministic runtime enforcement | prompt guard baseline vs runtime capability gate (optional/future unless implemented) |

## Step-by-Step Evaluation Pipeline
1. **Workload generation**
   - Load tasks from `configs/tasks/` and synthetic workloads from `configs/tasks_synth/`.
   - Attach attack-family and difficulty labels.
2. **Attack execution**
   - Execute each task under selected system mode (reference, baseline, or ablation).
3. **Policy enforcement**
   - Resolve runtime allow/deny decisions at the enforcement boundary.
4. **Trace logging**
   - Emit structured artifacts (`decision`, `rule_id`, `reason_code`, trace metadata).
5. **Metric computation**
   - Compute attack block rate, attack success rate, latency overhead, trace completeness, and decision-artifact coverage.
6. **Aggregation and reporting**
   - Aggregate by system/family/difficulty and generate paper-facing tables.

## Baseline Comparison Matrix
Primary baseline matrix:

\[
\text{baseline} \times \text{attack family} \times \text{difficulty level} \times \text{metric}
\]

## Ablation Study Methodology
To isolate why each control matters, evaluate targeted ablations that weaken one control at a time.

| Ablation mode | Component removed/weakened | Expected degradation | Metrics most affected |
|---|---|---|---|
| `full_system` | none (reference mode) | strongest blocking and trace quality | all metrics (reference) |
| `no_default_deny` | deny fallback removed/weakened | unsafe fallthrough on unmatched requests | ABR, ASR |
| `no_first_match_ordering` | deterministic first-match ordering removed | unstable/conflicting decisions on overlapping rules | ABR, ASR, explainability consistency |
| `no_trace` / `reduced_observability` | trace emission reduced/disabled | forensic visibility loss | TCR, SDAC |
| `no_capability_confinement` / `coarse_capability_gating` | fine-grained capability boundary weakened | privilege overreach | ABR, ASR |
| `no_enforcement` | enforcement bypassed | highest attack success | ABR, ASR |

## Full Experiment Matrix
\[
\text{system mode} \times \text{attack family} \times \text{difficulty level} \times \text{metric}
\]

Reporting views:
- overall baseline comparison,
- baseline breakdown by family,
- baseline breakdown by difficulty,
- ablation summaries,
- deltas versus `full_system`.

## Metrics
Primary metrics are defined in [METRICS](METRICS.md):
- attack block rate,
- attack success rate,
- latency overhead,
- trace completeness,
- structured decision artifact coverage.

## Repetitions and Aggregation
- Repeat runs across seeds/repetitions when available.
- Report mean and spread (std and/or confidence intervals).
- Generate tables deterministically from artifacts.
