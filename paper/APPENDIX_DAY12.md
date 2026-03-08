# Day 12 Appendix

| baseline | scenario_id | seeds | UER mean±std | FAR mean±std | TCR mean±std | EDS mean±std | plugin_loads mean±std | p50 latency mean±std | p95 latency mean±std |
|---|---|---:|---|---|---|---|---|---|---|
| default | scale_n200 | 5 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 0.00 ± 0.00 | 0.367 ± 0.074 | 0.587 ± 0.115 |
| no_plugin_isolation | scale_n200 | 5 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.00 ± 0.00 | 0.354 ± 0.084 | 0.603 ± 0.082 |
| no_policy | scale_n200 | 5 | 1.0000 ± 0.0000 | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 0.00 ± 0.00 | 0.236 ± 0.040 | 0.432 ± 0.147 |
| no_trace | scale_n200 | 5 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | 0.00 ± 0.00 | 0.122 ± 0.024 | 0.192 ± 0.035 |
| raw_errors | scale_n200 | 5 | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 0.00 ± 0.00 | 0.416 ± 0.075 | 0.611 ± 0.066 |

## Attack Success Rate Breakdown

Populate this section from existing benchmark matrix outputs. Do not manually synthesize values.

### ASR by Attack Family

| system | attack_family | Attack Success Rate ↓ | notes |
|---|---|---:|---|
| `default` | `prompt_injection` | `TBD` | from matrix family slice |
| `default` | `filesystem_damage` | `TBD` | from matrix family slice |
| `default` | `shell_misuse` | `TBD` | from matrix family slice |
| `default` | `data_exfiltration` | `TBD` | from matrix family slice |
| `default` | `network_exfiltration` | `TBD` | from matrix family slice |

### ASR by Scenario Difficulty

| system | scenario_difficulty | Attack Success Rate ↓ | notes |
|---|---|---:|---|
| `default` | `easy` | `TBD` | from matrix difficulty slice |
| `default` | `medium` | `TBD` | from matrix difficulty slice |
| `default` | `hard` / `multi_step` | `TBD` | from matrix difficulty slice |

## Real-Agent Case Study Details

The real-agent case study uses `examples/agent_integration/run_case_study.py` as a minimal tool-using agent harness. Prompts are mapped to concrete tool requests (`shell`, `http_request`, or `filesystem`) and routed through `ToolGateway` under two policy modes:
- restrictive policy (`allow_fs_http_deny_shell`),
- permissive control (`allow_all`).

Per-case reporting includes:
- tool request (`tool_name`, `capability`, `tool_args`),
- mediation decision (`allow` or `deny`),
- trace fields (`decision`, `tool_name`, `capability`, `reason`, timestamp and related identifiers).

This appendix section documents runtime mediation behavior at request level; it does not add new benchmark numbers beyond generated case-study artifacts.
