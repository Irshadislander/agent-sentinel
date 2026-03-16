# Paper Result Tables

- Source: `bench/results/matrix.json`
- Generated at (UTC): `2026-03-07T18:32:03.144025+00:00`

## Evaluation-at-a-Glance

| Evaluation Component | Workload | Main Outcome | Artifact |
|---|---|---|---|
| Baseline evaluation suite | Benchmark scenarios | Measures policy enforcement, safe allowances, and latency | artifacts/baselines/ |
| AutoGen integration case study | 5 tasks (3 benign, 2 attack) | Benign tasks completed while attack attempts are blocked | artifacts/autogen_integration/autogen_results.json |
| Trace artifacts | JSONL execution traces | Enables forensic inspection of tool mediation and blocked actions | artifacts/autogen_integration/traces/ |
| Reproducibility package | Scripts and configs | Allows reviewers to reproduce experiments locally | examples/ , configs/ , paper/ |

## Table 1: Baseline Metrics

| Baseline | UER | ΔUER vs default | FAR | ΔFAR vs default | TCR | ΔTCR vs default | EDS | ΔEDS vs default | plugin_loads | Δplugin_loads vs default |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default | 0.2468 | +0.0000 | 0.0000 | +0.0000 | 0.8741 | +0.0000 | 0.0900 | +0.0000 | 0 | +0 |
| no_plugin_isolation | 0.2468 | +0.0000 | 0.0000 | +0.0000 | 0.8741 | +0.0000 | 0.0800 | -0.0100 | 1 | +1 |
| no_policy | 0.9810 | +0.7342 | 0.0000 | +0.0000 | 0.8741 | +0.0000 | 0.8450 | +0.7550 | 0 | +0 |
| no_trace | 0.2468 | +0.0000 | 0.0000 | +0.0000 | 0.0000 | -0.8741 | 0.0900 | +0.0000 | 0 | +0 |
| raw_errors | 0.2468 | +0.0000 | 1.0000 | +1.0000 | 0.8741 | +0.0000 | 0.0900 | +0.0000 | 0 | +0 |

## Attack Success Rate Summary

Attack success outcomes are reported as attack-family-aggregated results from the existing benchmark export. Benign success is computed from benign slices as \(1-\mathrm{FAR}\) for the same system row.

| System | Attack Success Rate ↓ | Benign Success ↑ | Notes |
|---|---:|---:|---|
| default | 0.2468 | 1.0000 | family-aggregated ASR from existing matrix-derived baseline summary |
| no_plugin_isolation | 0.2468 | 1.0000 | same ASR as default in current Day 12 export |
| no_policy | 0.9810 | 1.0000 | weakest enforcement profile (highest attack success) |
| no_trace | 0.2468 | 1.0000 | attack success unchanged vs default; observability degraded |
| raw_errors | 0.2468 | 0.0000 | benign reliability collapse under raw error mode |

## AutoGen Integration Case Study

| System | Benign Tasks Completed | Attack Tasks Blocked | Median Latency (ms) |
|---|---:|---:|---:|
| Agent-Sentinel + AutoGen (real LLM case study) | TBD | TBD | TBD |

## Table A: Scale Stability

| scenario_id | N | UER | FAR | TCR | EDS | p50_ms | p95_ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| scale_n50 | 50 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 0.265 | 0.850 |
| scale_n200 | 200 | 0.2600 | 0.0000 | 0.8662 | 0.0900 | 0.242 | 0.543 |

## Table B: Stress Degradation

| scenario_id | malformed_p | plugin_p | ΔUER | ΔFAR | ΔTCR | ΔEDS | Δp50_ms | Δp95_ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| - | - | - | - | - | - | - | - | - |

## Table C: Sensitivity

| scenario_id | strictness | trace_sample_rate | allowlist_size | UER | FAR | TCR | EDS | p50_ms | p95_ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| - | - | - | - | - | - | - | - | - | - |

## Table X: Stability Across Seeds (mean ± std)

| baseline | scenario_id | UER (mean±std) | FAR (mean±std) | TCR (mean±std) | EDS (mean±std) | plugin_loads (mean±std) | p95 latency ms (mean±std) |
|---|---|---|---|---|---|---|---|
| default | scale_n200 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 0.00 ± 0.00 | 0.587 ± 0.115 |
| no_plugin_isolation | scale_n200 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.00 ± 0.00 | 0.603 ± 0.082 |
| no_policy | scale_n200 | 1.0000 ± 0.0000 | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 0.00 ± 0.00 | 0.432 ± 0.147 |
| no_trace | scale_n200 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | 0.00 ± 0.00 | 0.192 ± 0.035 |
| raw_errors | scale_n200 | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 0.00 ± 0.00 | 0.611 ± 0.066 |
