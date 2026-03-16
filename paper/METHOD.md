# Method

## System Overview
Agent-Sentinel is a runtime mediation layer placed between agent planning and tool execution. Each request is represented as:

\[
r = (\text{tool}, \text{args}, \text{context})
\]

The runtime resolves each request to `allow` or `deny` before any tool side effect occurs.

## Runtime Mediation Flow
1. The agent emits a tool request.
2. `ToolGateway` receives the request and resolves its required capability set.
3. `Policy Engine` evaluates ordered rules for the request context.
4. Capability and validator checks are applied.
5. The runtime emits an explicit `allow` or `deny` decision.
6. Tool execution proceeds only on `allow`; `deny` terminates the execution path.
7. A structured decision/trace artifact is emitted for every request.

## Policy Semantics
Policy evaluation is deterministic and fail-closed:
- rules are evaluated in defined order,
- first matching rule determines the decision,
- unmatched or incompatible paths resolve to `deny`.

This provides stable authorization semantics across repeated runs with identical inputs.

## Decision Artifacts
Each mediated request emits structured evidence for audit and debugging:
- `decision` (`allow` or `deny`),
- `rule_id` (when a rule match exists),
- `reason_code` / reason string,
- trace metadata (request/runtime context fields).

These artifacts support security metrics (for example block/success outcomes) and observability metrics (trace completeness and artifact coverage).

## Real-Agent Integration Path
The repository includes a minimal integration harness (`examples/agent_integration/run_case_study.py`) that simulates a tool-using agent loop. It demonstrates the full runtime path from prompt-derived request to gateway mediation, allow/deny decision, and trace emission.

## Boundary of Claims
Method claims are scoped to runtime mediation behavior under the declared threat model and trust assumptions. This method is not presented as a full sandbox or complete system-security replacement.

## Links
- [FORMAL_MODEL](FORMAL_MODEL.md)
- [THREAT_MODEL](THREAT_MODEL.md)
- [METRICS](METRICS.md)
- [RESULTS](tables/results_tables.md)
- [ROBUSTNESS](ROBUSTNESS.md)
- [PERF](PERF_DAYXX.md)
