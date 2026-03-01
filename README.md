# Agent Sentinel

## What Is Agent Sentinel
Agent Sentinel is a zero-trust runtime security layer for tool-using AI agents. It treats the planner as untrusted, enforces policy at a single gateway, and records tamper-evident JSONL ledgers so runs can be audited and verified.

## Features
- Capability-aware policy decisions at tool execution time.
- Tamper-evident flight recorder (hash-chained append-only ledger).
- Baseline vs secured benchmark runner with attack cases.
- Minimal Streamlit UI to browse runs and verify ledgers.

## Install
```bash
python -m pip install -e .
```

For developer + UI extras:
```bash
python -m pip install -e ".[dev,ui]"
```

## Quickstart
Run benchmark:
```bash
python -m agent_sentinel.benchmark.run_benchmark --policy configs/policies/default.yaml
```

Run UI:
```bash
python -m agent_sentinel.ui
```

Or use entrypoints after install:
```bash
agent-sentinel --policy configs/policies/default.yaml
agent-sentinel-ui
```

## Example Policy Snippet
```yaml
allowlist_domains:
  - api.github.com
  - raw.githubusercontent.com
default_allow: false
capabilities:
  fs.read.public: true
  fs.read.private: false
  fs.write.workspace: true
  net.http.get: true
  net.http.post: false
  net.external: false
```

## Repo Structure
```text
src/agent_sentinel/
  security/      # capabilities, policy, validators, gateway
  forensics/     # ledger + verification
  benchmark/     # attack suite + benchmark runners
  runtime/       # task/planner/runner
  tools/         # fs/http tool adapters
  ui/            # streamlit app
configs/
  policies/
  tasks/
tests/
```

## Dev Commands
```bash
ruff check .
ruff format .
mypy src/agent_sentinel || true
pytest -q
```
