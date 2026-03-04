# Agent Integration (Minimal Case Study)

This directory provides a dependency-light "mini-agent" harness that generates tool requests and routes them through Agent-Sentinel's runtime gate (ToolGateway).

## What it demonstrates
- Runtime capability gating (allow/deny) for tool calls
- Attack prompt that attempts to execute shell after a benign step
- Audit trace fields and a simple "trace completeness" score
- Latency overhead per decision (ms)

## Run
```bash
PYTHONPATH=src python3 examples/agent_integration/run_case_study.py
```

Outputs:
- `artifacts/agent_integration/case_study_results.json`
