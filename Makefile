.PHONY: install dev ui lint format type test bench bench-report run-ui clean

install:
	python -m pip install -U pip
	python -m pip install -e .

dev:
	python -m pip install -e ".[dev]"

ui:
	python -m pip install -e ".[ui]"

lint:
	ruff check .

format:
	ruff format .

type:
	mypy src/agent_sentinel || true

test:
	pytest -q

bench:
	PYTHONPATH=src python -m agent_sentinel.benchmark.run_benchmark

bench-report: bench
	PYTHONPATH=src python -m agent_sentinel.benchmark.report --input bench/results/latest.json --output docs/bench_report.md

run-ui:
	agent-sentinel-ui

clean:
	rm -rf build dist .pytest_cache
	rm -rf *.egg-info src/*.egg-info
