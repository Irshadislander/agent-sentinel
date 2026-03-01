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

## Troubleshooting (macOS + Python 3.14)

If `agent-sentinel-ui` or `agent-sentinel-benchmark` fails with `ModuleNotFoundError`
even after `pip install -e .`, macOS may have marked site-packages as hidden which
can prevent Python from applying editable `.pth` injection.

Fix:

```bash
source .venv/bin/activate
./scripts/macos_unhide_sitepackages.sh
```
