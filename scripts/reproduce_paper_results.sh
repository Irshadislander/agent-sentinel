#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

OUTPUT_DIR="bench/results"
TABLE_PATH="paper/results_tables.md"
BASELINES="default,no_policy,no_trace,raw_errors,no_plugin_isolation"

echo "[1/3] Running tests..."
PYTHONPATH=src python3 -m pytest -q

echo "[2/3] Running matrix benchmark baselines..."
PYTHONPATH=src python3 -m agent_sentinel.benchmark.run_benchmark \
  --matrix \
  --baselines "$BASELINES" \
  --output-dir "$OUTPUT_DIR"

echo "[3/3] Generating paper result tables..."
python3 scripts/generate_paper_tables.py \
  --matrix-input "$OUTPUT_DIR/matrix.json" \
  --output "$TABLE_PATH"

echo "Done."
echo "Matrix JSON: $ROOT_DIR/$OUTPUT_DIR/matrix.json"
echo "Matrix CSV:  $ROOT_DIR/$OUTPUT_DIR/matrix.csv"
echo "Paper table: $ROOT_DIR/$TABLE_PATH"
