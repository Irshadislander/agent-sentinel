.PHONY: fmt test bench report paper repro clean

# Format + lint
fmt:
	ruff format .
	ruff check . --fix

# Unit tests
test:
	pytest -q

# Policy engine microbenchmark (writes JSON + markdown outputs)
bench:
	python scripts/bench_policy_engine.py

# Canonical report generation (writes results_tables + perf md + robustness json)
report:
	python scripts/generate_canonical_report.py \
	  --matrix-input artifacts/bench/matrix.json \
	  --results-output paper/results_tables.md \
	  --policy-perf-json artifacts/bench/policy_engine_bench.json \
	  --policy-perf-markdown paper/PERF_DAYXX.md \
	  --robustness-output artifacts/bench/robustness_report.json

# (Optional) Regenerate paper tables/appendix/summary if your script exists on main
paper:
	python -u scripts/generate_paper_tables.py

# One command to reproduce the key evaluation artifacts
repro: fmt test bench report paper

# Clean local generated artifacts (safe to delete)
clean:
	rm -f artifacts/bench/latest.csv artifacts/bench/latest.json
	rm -f artifacts/bench/matrix.csv artifacts/bench/matrix.json
	rm -f artifacts/bench/robustness_report.json
	rm -f artifacts/bench/policy_engine_bench.json
