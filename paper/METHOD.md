# Method

## Runtime Capability Gating
Agent-Sentinel places enforcement on the runtime path between agent planning and tool execution. Requests are represented as:

\[
r = (\text{tool}, \text{args}, \text{context})
\]

Each tool is mapped to required capabilities. A request is allowed only when policy evaluation authorizes the required capability set for that request context.

## Policy Evaluation
Policy evaluation is deterministic and fail-closed:
1. load and validate policy input;
2. evaluate rules in defined order;
3. apply first matching rule decision;
4. apply default deny when no allow condition is satisfied.

This keeps authorization behavior stable across runs and prevents ambiguous fallback behavior.

## Decision Artifacts
Every decision emits structured artifacts for explainability and audit:
- `decision` (`allow` or `deny`),
- `rule_id` (matched rule identifier, when applicable),
- `reason_code` (decision rationale),
- trace metadata (request and runtime context fields).

These artifacts support downstream analysis of block rate, trace completeness, and decision coverage.

## Enforcement Pipeline
The runtime pipeline is:
1. agent produces tool request,
2. gateway performs capability and policy checks,
3. gateway emits decision artifact,
4. tool executes only on allow,
5. traces and metrics are aggregated for reporting.

This implementation-level pipeline aligns with the formal model and threat assumptions, while keeping claims scoped to runtime enforcement behavior.

## Ablation Hooks
Experimental toggles remove specific controls (`no_policy`, `no_trace`, `raw_errors`, `no_plugin_isolation`) to isolate causal effects on safety, observability, and performance without changing workload definitions.

## Links
- [FORMAL_MODEL](FORMAL_MODEL.md)
- [THREAT_MODEL](THREAT_MODEL.md)
- [METRICS](METRICS.md)
- [RESULTS](results_tables.md)
- [ROBUSTNESS](ROBUSTNESS.md)
- [PERF](PERF_DAYXX.md)
