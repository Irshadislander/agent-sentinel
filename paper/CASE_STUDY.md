# Case Study: Minimal Tool-Agent Integration

We include a minimal agent harness (no external framework dependency) that converts prompts into tool requests and routes every request through Agent-Sentinel's runtime gate (ToolGateway).

## Setup
This case study is a lightweight integration check aligned with the benchmark framing in [EVAL_PROTOCOL](EVAL_PROTOCOL.md). It validates runtime gating behavior and decision artifacts, but does not replace the full benchmark matrix.

Policy conditions in this micro-study:
- **P_safe**: allow filesystem + HTTP, deny shell (default deny).
- **P_perm**: permissive/allow-all style condition for shell-enabled behavior.

## Scenarios
Scenario mapping:
- **Benign control**: fetch and save flow.
- **Shell misuse attack** (`easy` / `medium` style): fetch then attempt shell execution.
- **Permissive policy control**: shell execution under `P_perm`.

Relation to workload taxonomy:
- This case study directly exercises one attack family (`shell_misuse`).
- Full benchmark coverage should include all five families:
  `prompt_injection`, `filesystem_damage`, `shell_misuse`, `data_exfiltration`, `network_exfiltration`.

Baseline framing:
- `P_safe` approximates enforced mode behavior in this minimal harness.
- `P_perm` approximates allow-all baseline behavior.
- no-enforcement, naive allow-list, and optional LLM-guard baselines are benchmark-level modes, not fully represented by this script alone.

## Metrics
We report:
- **Attack blocked rate**
- **Mean decision latency (ms)**
- **Mean trace completeness score** (fraction of required audit fields present)
- **Structured decision artifact presence** (`decision`, `rule_id`, `reason_code`, trace fields)

## Repro
```bash
PYTHONPATH=src python3 examples/agent_integration/run_case_study.py
cat artifacts/agent_integration/case_study_results.json
```

## Notes
This case study is intentionally minimal and benchmark-aligned. Its role is to sanity-check enforcement semantics before full adversarial matrix runs.
