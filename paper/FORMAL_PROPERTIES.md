# Formal Safety Properties

This section states runtime safety properties for Agent-Sentinel's capability-gating model.
Claims are scoped to enforcement behavior and supported by proof sketches and implementation logic, not full mechanized proofs.

## Notation
Fix request universe \(U\), policy \(P\), and deterministic decision function \(D_P(r) \in \{\text{allow}, \text{deny}\}\).

- \(r\): request `(tool, args, context)`
- \(\mathrm{Req}(r)\): capability requirements of \(r\)
- \(G_P(r)\): capabilities granted to \(r\) by policy/runtime state
- \(\mathrm{Allowed}(P)=\{r \in U \mid D_P(r)=\text{allow}\}\)

## P1. Safety Monotonicity
### Statement
Let \(P'\) be a restrictive refinement of \(P\): it may add deny rules and/or remove grants, but does not add new allow behavior on \(U\).
Then:

\[
\mathrm{Allowed}(P') \subseteq \mathrm{Allowed}(P)
\]

### Interpretation
Hardening policy cannot expand the allowed runtime action surface.

### Proof Sketch
1. For fixed inputs, resolution is deterministic.
2. Restrictive refinement removes or preserves allow paths.
3. Default deny prevents unmatched requests from becoming implicitly allowed.
Therefore the allow set is monotone non-increasing under restrictive refinements.

## P2. Capability Confinement
### Statement
If a request requires a capability that is not granted, the request cannot be successfully executed:

\[
\mathrm{Req}(r) \nsubseteq G_P(r) \Rightarrow D_P(r)=\text{deny}
\]

and the runtime blocks tool execution.

### Interpretation
This is an enforcement-path guarantee at runtime boundaries. It is not a statement about what the model may attempt or reason about.

### Proof Sketch
1. Request capability requirements are checked against granted capabilities.
2. Missing capability produces deny.
3. Deny path terminates before tool call execution.

## P3. Capability Non-Interference (Scoped)
### Statement
For independent capabilities \(c_i\) and \(c_j\), \(c_i \neq c_j\), if policy edits from \(P\) to \(P'\) affect only rules/grants for \(c_j\), then decisions for requests requiring only \(c_i\) are unchanged:

\[
\forall r_i \in U,\ \mathrm{Req}(r_i)=\{c_i\} \Rightarrow D_P(r_i)=D_{P'}(r_i)
\]

### Scope
This is scoped to unchanged request contexts and matching logic, and to capability dimensions intended to be independent in policy design.

### Interpretation
Editing one capability policy should not cause unrelated capability regressions.

## Minimal Counterexamples and Prevention
### CE1: No Default Deny
Unsafe behavior: unmatched `shell.exec` request falls through to allow.

Agent-Sentinel prevention: unmatched requests resolve to explicit deny with reason code.

### CE2: Missing Capability Confinement
Unsafe behavior: system checks prompt text only; `filesystem.write` executes without write grant.

Agent-Sentinel prevention: capability mismatch produces deny and blocks pre-execution.

### CE3: Capability Coupling Side Effect
Unsafe behavior: changing `network.http` policy unintentionally alters `filesystem.read` decisions.

Agent-Sentinel prevention: deterministic capability-scoped rule evaluation limits cross-capability interference under scoped edits.

## Implementation Mapping

| Property | Runtime Mechanism | Implementation Anchor | Decision Evidence |
|---|---|---|---|
| Safety Monotonicity | deterministic ordered rule resolution + default deny | `policy_engine.resolve_decision`, rule ordering in policy parsing/evaluation | stable allow/deny class under restrictive policy edits |
| Capability Confinement | pre-execution capability check at gateway boundary | `ToolGateway.execute`, capability checks via `caps.granted` and policy resolver | deny path with no successful tool execution |
| Capability Non-Interference (scoped) | capability-scoped matching with deterministic evaluation | policy rule capability fields + gateway/policy capability mapping | unchanged decisions for unrelated capability requests under scoped edits |

Structured artifacts (`decision`, `rule_id`, `reason_code`, trace metadata) support auditing of these properties.
