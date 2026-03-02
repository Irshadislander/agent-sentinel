.PHONY: install dev ui lint format type test bench ci run-ui clean

install:
	python -m pip install -U pip
	python -m pip install -e .

dev:
	python -m pip install -e ".[dev]"

ui:
	python -m pip install -e ".[ui]"

lint:
	pre-commit run --all-files

format:
	ruff format .

type:
	mypy src/agent_sentinel || true

test:
	python -m pytest -q

bench:
	PYTHONPATH=src python -m bench.run_bench || python bench/run_bench.py

ci:
	$(MAKE) lint
	$(MAKE) test

run-ui:
	agent-sentinel-ui

clean:
	rm -rf build dist .pytest_cache
	rm -rf *.egg-info src/*.egg-info
