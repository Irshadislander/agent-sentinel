# Formal Capability Execution Model

## 1. System Model
We model a tool-augmented runtime with four objects:

- Agent \(A\): emits tool requests.
- Tool set \(T\): executable tool interfaces.
- Capability set \(C\): atomic permissions enforced at runtime.
- Policy \(P\): ordered rules that map requests to decisions.

A runtime request is:

\[
r = (\text{tool}, \text{args}, \text{context})
\]

where \(\text{tool} \in T\), `args` is structured input, and `context` is request metadata.

The runtime decides before execution:

\[
D_P(r) \in \{\text{allow}, \text{deny}\}
\]

## 2. Capability Model
A capability is an element \(c \in C\). Example capability names:

- `filesystem.read`
- `filesystem.write`
- `network.http`
- `shell.exec`

Each request has required capabilities:

\[
\mathrm{Req}(r) \subseteq C
\]

The request can execute only when required capabilities are granted by policy/runtime state.

## 3. Policy Model
Policy \(P\) is an ordered sequence:

\[
P = [\rho_1,\rho_2,\dots,\rho_n]
\]

Each rule \(\rho_i\) includes:

- `rule_id`
- capability requirements
- optional conditions over `(tool, args, context)`
- decision in `{allow, deny}`

Functional view:

\[
P : (\text{tool}, \text{args}, \text{context}) \rightarrow \{\text{allow}, \text{deny}\}
\]

Resolution is deterministic first-match:

1. evaluate rules in order,
2. pick the first matching rule,
3. return that rule's decision,
4. if no rule matches, return `deny` (default deny).

### 3.1 Policy Composition (Scoped)
For two policies \(P_a\) and \(P_b\), composition is defined over the same request form
\(r=(\text{tool},\text{args},\text{context})\).

Let \(K(r;P_a,P_b)\in\{\text{true},\text{false}\}\) be a compatibility predicate
(for example, aligned capability naming and request-to-capability mapping).

\[
D_{P_a \otimes P_b}(r)=
\begin{cases}
\text{allow}, & \text{if } D_{P_a}(r)=\text{allow} \land D_{P_b}(r)=\text{allow} \land K(r;P_a,P_b) \\
\text{deny}, & \text{otherwise}
\end{cases}
\]

This is fail-closed: disagreement or incompatibility resolves to `deny`.

## 4. Enforcement Semantics
Let \(G_P(r) \subseteq C\) denote capabilities granted to request \(r\) under policy \(P\).

\[
D_P(r)=
\begin{cases}
\text{allow}, & \text{if } \mathrm{Req}(r) \subseteq G_P(r) \\
\text{deny}, & \text{otherwise}
\end{cases}
\]

Runtime semantics are pre-execution: denied requests are blocked before tool side effects.

Default deny applies when:

- no rule matches,
- policy is missing/invalid,
- request class cannot be mapped to an allowed capability path.

## 5. Safety Properties (Scoped)
We use four scoped properties:

### P1. Safety Monotonicity
Restrictive policy refinements cannot increase the allowed request set.

\[
\mathrm{Allowed}(P') \subseteq \mathrm{Allowed}(P)
\]

for policy refinements \(P'\) that only add denials/remove grants.

### P2. Capability Confinement
If a request requires an ungranted capability, it is denied and not executed.

\[
\mathrm{Req}(r) \nsubseteq G_P(r) \Rightarrow D_P(r)=\text{deny}
\]

This is a runtime enforcement property, not a claim about model intent.

### P3. Capability Non-Interference (Scoped)
Policy changes for one independent capability should not alter decisions for an unrelated capability (under unchanged context/matching logic).

\[
D_P(r_i) = D_{P'}(r_i)
\]

for requests \(r_i\) that require only capability \(c_i\), when edits from \(P\) to \(P'\) affect only capability \(c_j \neq c_i\).

### P4. Policy Composability (Scoped)
Under deterministic mediation, ordered rule evaluation, and default-deny fallback, policy composition cannot expand the allow set beyond compatible intersection:
\[
\mathrm{Allowed}(P_a \otimes P_b) \subseteq \mathrm{Allowed}(P_a)\cap \mathrm{Allowed}(P_b)\cap \mathrm{Compat}(P_a,P_b)
\]
where \(\mathrm{Compat}(P_a,P_b)\) is the set of requests satisfying \(K\).

## 6. Decision Artifacts
Each decision emits structured evidence:

- `decision`
- `rule_id`
- `reason_code`
- trace metadata

These artifacts make runtime behavior auditable and explainable.

## 7. Connection to Implementation
The model maps directly to repository components:

- `ToolGateway` (`src/agent_sentinel/security/tool_gateway.py`): runtime enforcement boundary before tool execution.
- Policy resolver (`src/agent_sentinel/security/policy_engine.py`): ordered matching, deterministic decision, default-deny outcomes.
- Capability set (`caps.granted` and capability checks in gateway/policy logic): request-to-capability gating.
- Flight recorder / ledger (`src/agent_sentinel/forensics/ledger.py`): append-only decision/event evidence.

See [FORMAL_PROPERTIES](FORMAL_PROPERTIES.md) for tightened property statements, proof sketches, and minimal counterexamples.
