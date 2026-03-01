# Agent-Sentinel Architecture (Zero-Trust Agent Runtime)

## Principle
Treat the LLM as an untrusted planner. All actions must pass through a ToolGateway that enforces capability-based policy and produces tamper-evident forensics.

## Components
- AgentRunner: orchestrates plan -> propose tool calls -> execution loop
- ToolGateway: single choke point for all tool calls (policy + validation)
- PolicyEngine: capability model (least privilege, default deny)
- Sandbox: constrained execution environment (v1: workspace scoping; v2: Docker)
- Flight Recorder: append-only, hash-chained action log + verification
- Benchmark Harness: baseline vs secured evaluation suite
- Minimal UI: policy viewer + run explorer + log verification status

## Data Flow
LLM (planner) -> AgentRunner -> ToolGateway -> Tool -> ToolGateway -> FlightRecorder

## Non-negotiables
- Default deny for external network
- All tools executed only via ToolGateway
- Hash-chained logs with verification CLI
- Reproducible benchmark runner
