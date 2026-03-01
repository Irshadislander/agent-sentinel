# agent-sentinel

Policy-enforced tool gateway + benchmark harness + run ledger + Streamlit run browser.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev,ui]"
```

Run benchmark

```bash
agent-sentinel-benchmark --policy configs/policies/default.yaml
```

Run UI

```bash
agent-sentinel-ui
# open http://localhost:8501
```

Dev checks

```bash
ruff check . --fix
ruff format .
pytest -q
mypy src/agent_sentinel || true
```

Note on src/ layout

This repo uses src/ layout. A small sitecustomize.py is included to make
import agent_sentinel reliable when running from the repo root.
