# Evaluation Harness

## Purpose

The benchmark harness provides reproducible latency measurements for key runtime paths:
- CLI cold start
- CLI warm start
- Registry/plugin discovery
- Payload validation
- Trace/observability write overhead
- End-to-end capability execution
- Trace view command latency

Outputs are written in machine-friendly formats for plotting and trend tracking.

## Run

```bash
python bench/run_bench.py
```

Optional flags:

```bash
python bench/run_bench.py --iterations 50 --capability-id core.example.echo --output-dir bench/results
```

## Output Files

The harness writes:
- `bench/results/latest.json`
- `bench/results/latest.csv`

`latest.json` contains:
- generation timestamp
- iteration count
- metric sample arrays
- summary stats (`mean`, `p50`, `p95`, `min`, `max`, `std`)

`latest.csv` contains one row per metric with summary values.

## Interpreting Results

- `cli_cold_start_ms`: first CLI command invocation latency in a fresh subprocess.
- `cli_warm_start_ms`: subsequent list command latency (hot filesystem/import caches).
- `registry_plugin_discovery_ms`: discovery + load time for entrypoint plugins.
- `payload_validation_ms`: schema validation function overhead.
- `trace_observability_overhead_ms`: append cost for one trace JSONL event.
- `capability_execution_e2e_ms`: total CLI `run` command latency.
- `cli_trace_view_ms`: latency of listing the latest trace events.

Use `p95` to track tail behavior and compare across commits.

## Expected Overhead Sources

- Payload validation:
  - schema checks
  - required-field checks
- Plugin discovery:
  - entrypoint enumeration
  - plugin import/registration
- Observability:
  - trace event serialization
  - file append I/O
- CLI runtime:
  - Python process startup
  - argument parsing
  - command dispatch
