# Paper Artifacts

This directory contains manuscript sections and paper-facing artifacts for Agent-Sentinel.

## Overleaf-Ready Assets (Primary)

Copy these folders first when assembling the paper package:

- `paper/tables/` — paper tables (for example `table_baselines.md`, `table_asr.md`, `table_results_day12.md`, `table_appendix_day12.md`)
- `paper/figures/` — paper figures and diagrams (for example architecture, baseline comparison, trace tradeoff, latency tradeoff)

These are the primary Overleaf-ready assets.

## Supporting Benchmark Outputs

Generated benchmark outputs live under `artifacts/bench/` and serve as source artifacts for the paper tables/figures:

- `artifacts/bench/matrix.json`
- `artifacts/bench/policy_engine_bench.json`
- `artifacts/bench/robustness_report.json`

The real-agent integration case study output is written to:

- `artifacts/agent_integration/case_study_results.json`

## Core Manuscript Files

- `ABSTRACT.md`
- `INTRO.md`
- `METHOD.md`
- `THREAT_MODEL.md`
- `METRICS.md`
- `EXPERIMENTS.md`
- `results_tables.md` (legacy consolidated table file)
- `CONCLUSION.md`

## Reproduce Evaluation Artifacts

From repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m agent_sentinel.benchmark.run_benchmark --matrix --matrix-all-baselines --output-dir artifacts/bench
python scripts/generate_paper_tables.py
python scripts/generate_figures.py
PYTHONPATH=src python examples/agent_integration/run_case_study.py
```

## Notes

- Paper-facing assets are generated from benchmark outputs; do not manually invent values.
- Claims are scoped to runtime mediation under the threat model assumptions.
