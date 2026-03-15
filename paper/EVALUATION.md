# Evaluation

## Results Overview

| Attack Family | Unsafe Actions Blocked (%) | Safe Actions Allowed (%) | Median Decision Latency (ms) |
|---|---|---|---|
| Prompt Injection | TBD | TBD | TBD |
| Tool Misuse | TBD | TBD | TBD |
| Capability Escalation | TBD | TBD | TBD |
| Unauthorized API | TBD | TBD | TBD |
| Malicious System Commands | TBD | TBD | TBD |
| **Overall (75 scenarios)** | TBD | TBD | TBD |

This table is intended to surface the main evaluation outcomes once the baseline results are populated. In particular, it summarizes whether Agent-Sentinel blocks the majority of unsafe tool invocations, whether legitimate tool usage remains mostly unaffected, and whether the runtime mediation overhead remains small.

## Real-Agent Integration Case Study

We also include an AutoGen integration case study in which Agent-Sentinel mediates tool calls at runtime. The experiment wraps `search_web`, `read_file`, `write_file`, and `api_call` with a mediation step before execution.

The evaluation contains both benign tasks and attack tasks. Benign tasks exercise allowed file reads, workspace writes, paper search, and allowlisted API requests. Attack tasks attempt to read `/etc/passwd` and exfiltrate data to a malicious API endpoint. The case study can also be executed in a real LLM-backed AutoGen mode and is reported as a small real-agent case study separate from the main synthetic benchmark. All attack scenarios in this evaluation are simulated and are used only to measure defensive blocking behavior. Results are recorded in `artifacts/autogen_integration/autogen_results.json`.
