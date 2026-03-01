# Agent-Sentinel

**Agent-Sentinel** is a zero-trust runtime security layer for tool-using AI agents.
It enforces **capability-based permissions** at the tool boundary and records **tamper-evident forensic logs** (“flight recorder”) to mitigate indirect prompt injection, data exfiltration, and tool abuse.

## Core Ideas
- LLM is an **untrusted planner**
- All actions go through a **ToolGateway** (single choke point)
- **Default deny** external network and sensitive data reads
- **Tamper-evident logs** with hash chaining + verification
- Benchmark suite for **baseline vs secured** evaluation

## Repo Layout
- `src/agent_sentinel/` core runtime
- `docs/` architecture + notes
- `configs/` policies and task specs
- `tests/` unit/integration tests

## Status
Under active development (v1).
