.PHONY: fmt test bench matrix report paper repro clean

fmt:
	ruff format .
	ruff check . --fix

test:
	pytest -q

bench:
	python3 scripts/bench_policy_engine.py

matrix:
	PYTHONPATH=src python3 -m agent_sentinel.benchmark.run_benchmark --matrix --output-dir artifacts/bench

report:
	python3 scripts/generate_canonical_report.py \
	  --matrix-input artifacts/bench/matrix.json \
	  --results-output paper/results_tables.md \
	  --policy-perf-json artifacts/bench/policy_engine_bench.json \
	  --policy-perf-markdown paper/PERF_DAYXX.md \
	  --robustness-output artifacts/bench/robustness_report.json

paper:
	python3 scripts/generate_paper_tables.py

repro: fmt test bench matrix report paper

clean:
	rm -f artifacts/bench/latest.* artifacts/bench/matrix.* artifacts/bench/robustness_report.json artifacts/bench/policy_engine_bench.json
