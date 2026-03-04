# Case Study: Minimal Tool-Agent Integration

We include a minimal agent harness (no external framework dependency) that converts prompts into tool requests and routes every request through Agent-Sentinel's runtime gate (ToolGateway).

## Setup
We evaluate two policies:

- **P_safe**: allow filesystem + HTTP, deny shell (default deny)
- **P_perm**: allow filesystem + HTTP + shell (default deny)

## Scenarios
- **Benign**: fetch data and save it (no shell)
- **Attack**: fetch data then attempt a shell execution step
- **Permissive**: shell allowed under P_perm

## Metrics
We report:
- **Attack blocked rate**
- **Mean decision latency (ms)**
- **Mean trace completeness score** (fraction of required audit fields present)

## Repro
```bash
PYTHONPATH=src python3 examples/agent_integration/run_case_study.py
cat artifacts/agent_integration/case_study_results.json
```

## Notes
This case study is intentionally minimal; it exists to validate that enforcement semantics and audit traces remain consistent when embedded in an agent loop.
