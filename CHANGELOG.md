# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## Unreleased

## [0.1.5] - 2026-03-02

### Added
- Capability registry hardening and CLI capability dispatch coverage for list/run flows.
- Plugin discovery controls for safer loading (allowlist-aware behavior and core-only mode support).
- Observability and trace benchmarking documentation for repeatable latency checks.

### Changed
- Benchmark outputs under `bench/results/` are now treated as generated artifacts (ignored in git and published by CI artifact upload).

## [0.1.4] - 2026-03-02

### Added
- Structured policy error system with dedicated exception types and richer fields.
- Integration simulation harness for tool-using agent runtime enforcement.
- CLI UX improvements: structured error rendering, JSON mode, and exit codes.
- Enterprise capability registry with metadata (category, risk, description).
- Deterministic benchmarking baseline with CLI benchmark mode and JSON output.

## v0.1.3
- Added: edge-case tests for policy engine

## v0.1.2
- Release automation: tag-based GitHub Release workflow
- Added changelog + improved release checklist

## [0.1.1] - 2026-03-01

### Added
- Pre-commit hooks (ruff + format).
- CI strict lint/format enforcement.
- Release checklist docs and README release section.

### Fixed
- Ruff SIM101/SIM103 simplifications in policy engine.

## [0.1.0] - 2026-02-28

### Added
- Capability registry foundation with metadata-backed registration and deterministic lookup.
- CLI capability commands (`capabilities list`) and capability execution (`run CAPABILITY_ID --payload ...`).
- Trace/audit basics with structured JSON events and per-call runtime metadata.
- Strict policy schema validation and stable CLI exit-code/error payload behavior.
