.PHONY: install dev lint format type test bench ui

install:
	python -m pip install -e .

dev:
	python -m pip install -e ".[dev,ui]"

lint:
	ruff check .

format:
	ruff check . --fix
	ruff format .

type:
	mypy src/agent_sentinel || true

test:
	pytest -q

bench:
	python -m agent_sentinel.benchmark.run_benchmark --policy configs/policies/default.yaml

ui:
	python -m agent_sentinel.ui
