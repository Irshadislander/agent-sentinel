# Agent-Sentinel

**Agent-Sentinel** is a zero-trust runtime security layer for tool-using AI agents.
It enforces **capability-based permissions** at the tool boundary and records **tamper-evident forensic logs** (“flight recorder”) to mitigate indirect prompt injection, data exfiltration, and tool abuse.

## Core Ideas
- LLM is an **untrusted planner**
- All actions go through a **ToolGateway** (single choke point)
- **Default deny** external network and sensitive data reads
- **Tamper-evident logs** with hash chaining + verification
- Benchmark suite for **baseline vs secured** evaluation

## Repo Layout
- `src/agent_sentinel/` core runtime
- `docs/` architecture + notes
- `configs/` policies and task specs
- `tests/` unit/integration tests

## Status
Under active development (v1).

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev,ui]"
pytest -q
agent-sentinel-benchmark --policy configs/policies/default.yaml
agent-sentinel-ui
```

## Troubleshooting (macOS + Python 3.14)

If you see `ModuleNotFoundError: No module named agent_sentinel` after an editable install,
run:

```bash
./scripts/macos_unhide_sitepackages.sh
```
