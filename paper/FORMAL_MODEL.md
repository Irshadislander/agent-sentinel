# Formal Capability Execution Model

## 1. Problem Setting
Tool-using AI agents issue runtime requests to perform capability-bound actions (filesystem, network, or other external effects). The system objective is to enforce an allowlist-only policy with deterministic decision semantics and traceable outcomes for every request.

We model execution as a guarded transition in which enforcement must precede capability execution. The desired properties are:
- strict allow/deny enforcement,
- deterministic failure classes,
- auditable traces for post-hoc analysis.

## 2. Notation
- Capability identifier: \( c \in C \), where \( C \) is the set of canonical capability strings.
- Policy: \( P \), an allowlist policy definition.
- Request context: \( x \), containing `request_id`, `correlation_id`, `source`, and `timestamp`.
- Decision: \( d \in \{\text{allow}, \text{deny}\} \).
- Trace event: \( \tau \), a structured audit record emitted per request.
- Exit code: \( e \), a deterministic code class indicating outcome type.

## 3. Definitions
### Definition 1 (Capability)
A capability is a canonical identifier \( c \) with optional metadata (e.g., namespace, version, description, tags). Canonical IDs are the enforcement keys.

### Definition 2 (Policy)
A policy \( P \) is an allowlist-only mapping from request context class to decision. If no allow rule applies, decision is deny.

### Definition 3 (Enforcement Function)
\[
\mathrm{Enforce}(P, c, x) \rightarrow (d, e, \tau)
\]
where:
- \( d \) is the allow/deny decision,
- \( e \) is the associated exit-code class,
- \( \tau \) is the emitted trace event.

### Definition 4 (Violation)
A violation occurs when enforcement returns deny due to one of:
- unknown capability,
- invalid policy format,
- policy violation (capability not permitted under \( P \)).

## 4. Invariants and Guarantees
### G1. Policy Precedence
Enforcement is evaluated before any capability body executes.

### G2. Default Deny
If policy is missing, malformed, or non-applicable, the decision is deny with a specific structured error class.

### G3. Trace Completeness
Each request emits exactly one terminal trace event representing its effective outcome class.

### G4. Deterministic Exit Semantics
For the same \((P, c, x)\) class, enforcement produces the same exit-code category.

### G5. Non-Bypassability
A denied request cannot invoke capability execution through the standard runtime path.

## 5. What Is Novel
The contribution is not a command-line wrapper; it is an explicit execution semantics with measurable security invariants. The system defines a formal enforcement function, attaches deterministic error/exit behavior, and provides benchmark-compatible observability outputs suitable for controlled baseline comparisons.
