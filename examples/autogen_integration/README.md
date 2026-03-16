# AutoGen Integration

This directory contains a two-mode AutoGen integration case study for Agent-Sentinel. The runner supports a lightweight `compat_shim` mode and a `real_llm` mode that uses AutoGen with an OpenAI-backed model client.

## How it works

- The script loads `tasks.json` and executes the task set sequentially.
- Every tool request for `search_web`, `read_file`, `write_file`, and `api_call` is routed through `sentinel.mediate(tool_name, args)` before execution.
- If mediation returns `DENY`, the tool returns a `[BLOCKED] ...` message instead of executing.
- Results are written to a single machine-readable artifact with per-task completion, block counts, and latency summaries.

## Compat Shim Mode

```bash
AUTOGEN_BACKEND=compat_shim \
PYTHONPATH=src \
python3 examples/autogen_integration/run_autogen_sentinel.py
```

## Real LLM Mode

```bash
export AUTOGEN_BACKEND=real_llm
export OPENAI_API_KEY=your_api_key_here
export OPENAI_MODEL=gpt-4o-mini
PYTHONPATH=src python3 examples/autogen_integration/run_autogen_sentinel.py
```

If `AUTOGEN_BACKEND=real_llm` is selected and AutoGen or OpenAI credentials are not available, the script fails with a clear setup error instead of silently falling back.

## Output

- `artifacts/autogen_integration/autogen_results.json`
- `artifacts/autogen_integration/traces/*.jsonl`
- `artifacts/autogen_integration/workdir/`
