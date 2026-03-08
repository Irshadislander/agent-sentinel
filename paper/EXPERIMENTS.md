# Experiments (Final Reporting Map)

## 1. Evaluation Scope
We evaluate runtime capability mediation across:
- security effectiveness,
- performance overhead and scaling,
- observability quality.

Primary security outcome metrics are:
- **Attack Success Rate (ASR)**,
- **Attack Block Rate (ABR)**.

## 2. Systems Compared
### Reference
- `full_system`

### Baselines
- `no_enforcement`
- `allow_all`
- `naive_allow_list`
- `llm_guard_style` (optional/future unless implemented)

### Ablations
- `no_default_deny`
- `no_first_match_ordering`
- `no_trace` / `reduced_observability`
- `no_capability_confinement`
- `no_enforcement`

Unimplemented optional modes are reported as `NA`.

## 3. Benchmark Matrix (Source of Final Tables)
\[
\text{attack family} \times \text{difficulty level} \times \text{baseline/ablation} \times \text{metric}
\]

Final paper tables are derived from matrix outputs (for example `matrix.json` / `matrix.csv` style summaries), not manual aggregation.

## 4. Workload Axes
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

## 5. Production Agent Relevance
This benchmark is designed to approximate common tool-use patterns in production-oriented agent stacks without claiming direct production deployment. In particular, the scenarios model:
- tool invocation chains across multiple steps,
- filesystem access attempts,
- shell execution attempts,
- data exfiltration attempts (local and network-mediated).

The runtime mediation surface aligns with common integration points in:
- LangChain-style tool agents,
- OpenAI tool-calling runtimes,
- multi-agent orchestration systems.

## 6. Real Agent Evaluation
We include a minimal real-agent integration case study in `examples/agent_integration/run_case_study.py`. The harness simulates a tool-using agent loop: a prompt is converted to a tool request, the request is routed through `ToolGateway`, and the runtime returns an allow/deny outcome.

The case study evaluates both safe and unsafe actions:
- safe behavior: benign fetch/save-style requests under a restrictive policy,
- unsafe behavior: shell-execution attempts after benign steps,
- control condition: permissive policy mode where shell is intentionally allowed.

This section is intended as a runtime mediation demonstration, not a framework-scale deployment claim. The key artifact is the per-request decision/trace output emitted by the mediation path.

## 7. Table-to-Matrix Correspondence

- **Overall Baseline Comparison**: aggregate over all families and difficulties by baseline.
- **Attack Success Rate Summary**: aggregate ASR across attack families by system, with companion benign success.
- **Attack Family Summary**: aggregate over difficulties for each family.
- **Difficulty-Level Summary**: aggregate over families for each difficulty tier.
- **Security–Performance Summary**: join security deltas with latency/throughput deltas by baseline.
- **Ablation Summary**: aggregate ablation deltas vs `full_system`.

## 8. Execution Procedure
1. Load tasks from benchmark configs.
2. Label each task by family and difficulty.
3. Execute each slice across baselines/ablations.
4. Collect decisions, latency, throughput, and trace artifacts.
5. Aggregate to matrix outputs.
6. Render paper-facing tables from those outputs.

## 9. Statistical Reporting
- report mean and 95% confidence intervals,
- keep workload slices identical across compared systems,
- preserve reproducible artifact generation.
