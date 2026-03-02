# Agent-Sentinel Architecture

## System Boundaries

### Core types (`src/agent_sentinel/capabilities/base.py`)
- `CapabilitySpec`: immutable contract for capability identity, version, schema, and entrypoint.
- `Capability`: execution interface (`execute(payload) -> Result`).
- `Result`: normalized outcome envelope (`ok`, `code`, `data`, `error`, `metadata`).
- `ExitCode`: stable numeric status contract used across CLI and tests.

### Registry and discovery (`src/agent_sentinel/capabilities/registry.py`, `plugins.py`)
- `CapabilityRegistry` is the source of truth for loaded capabilities.
- Registration enforces invariants (unique ID, semver version, JSON-schema-like payload schema, required metadata).
- Plugin discovery uses Python entry points under `agent_sentinel.capabilities`.
- Plugin load behavior is fail-open by default (warn + continue) or fail-fast with `--strict-plugins`.

### CLI adapter layer (`src/agent_sentinel/cli.py`)
- CLI is an adapter over registry + validation + execution + tracing.
- Command modes:
  - `capabilities list`
  - `run CAPABILITY_ID --payload ...`
  - `trace view --last N`
- CLI does not own business logic for capability behavior; it delegates to registered capabilities.

### Tracing / observability (`src/agent_sentinel/observability.py`)
- `RunContext` captures reproducibility metadata (`run_id`, `correlation_id`, `timestamp`, `git_sha`, `user`, `host`).
- Each capability invocation emits a structured trace event (JSONL) with validation + runtime outcome fields.
- `TraceStore` persists trace events and supports bounded reads (`read_last`).

## Design Invariants
- Capability IDs are globally unique within a process.
- Capability versions must be semver-compatible.
- Capability schemas are required and validated at registration time.
- Registry listing and table output are deterministic.
- CLI output for machine consumers is explicit (`--emit-json`) and stable.
- Trace writes must be append-only and side-effect free for command correctness.

## Failure Modes
- Invalid capability registration:
  - duplicate IDs/names
  - invalid semver
  - missing/blank metadata
  - non-schema payload definitions
- Plugin loading failures:
  - malformed entrypoint object
  - import/load exceptions
  - unsupported plugin object shape
- Runtime execution failures:
  - payload parse errors
  - payload/schema validation errors
  - capability execution exceptions
- Trace read/write issues:
  - missing trace file
  - malformed JSON lines (ignored during reads)

## Operational Notes
- Default CLI path should be deterministic and network-independent for tests.
- Plugin loading can be disabled with `--no-plugins` for locked-down runs.
- Allowlist mode (`--plugins FILE`) constrains discovered plugins to explicit names.
