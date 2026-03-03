# Formal Capability Execution Model

## 1. Problem Setting
Tool-using agents request capabilities at runtime. The enforcement objective is to decide
allow/deny before execution, emit a traceable decision path, and preserve deterministic
outcomes for fixed inputs.

## Formal Objects

- Capability: a string identifier \(c \in \mathcal{C}\) describing an action (e.g., "fs.read", "http.request").
- Policy: a structured document \(P\) that defines a finite rule set \(R(P) = \{r_1,\dots,r_n\}\).
- Rule: \(r = (\text{id}, \text{action}, \text{capabilities}, \text{predicate})\) where:
  - id is a stable identifier
  - action ∈ {allow, deny, require_approval, allow_with_redaction}
  - capabilities is a set of capability identifiers
  - predicate is an optional match function over request context
- Request context: \(x\) is metadata about the request (tool name, arguments, caller identity, environment).
- Decision function:
  \[
    D(c, P, x) \to (\text{verdict}, \text{rule\_id}, \text{reason\_code}, \text{trace})
  \]

## Matching and Precedence

A rule r matches (c, x) if:
1) c ∈ r.capabilities, and
2) r.predicate(x) is true (or predicate is absent).

Let M be the ordered list of matching rules in policy order.
Precedence is:
1) If any matching deny exists → verdict = deny (choose first deny in policy order)
2) Else if any matching require_approval exists → verdict = require_approval
3) Else if any matching allow_with_redaction exists → verdict = allow_with_redaction
4) Else if any matching allow exists → verdict = allow
5) Else → default deny

## 4. Decision Semantics

Given \((c, P, x)\), evaluation is:

1. Parse and validate policy document.
2. If policy is missing/invalid, return deny with stable reason code.
3. Evaluate rules in policy order to produce the matching set \(M\).
4. Apply precedence over \(M\) to select a unique verdict and rule identifier.
5. Emit an ordered trace ending with a terminal resolution marker.

## 5. Outcome-to-Reason Mapping

| Outcome class | verdict | rule_id | reason_code |
|---|---|---|---|
| Policy missing | deny | None | `POLICY_MISSING` |
| Policy invalid | deny | None | `POLICY_INVALID` |
| Matching deny rule | deny | matched id | `RULE_DENY_MATCH` |
| Matching require_approval rule | require_approval | matched id | `RULE_REQUIRE_APPROVAL_MATCH` |
| Matching allow_with_redaction rule | allow_with_redaction | matched id | `RULE_ALLOW_WITH_REDACTION_MATCH` |
| Matching allow rule | allow | matched id | `RULE_ALLOW_MATCH` |
| No rule match | deny | None | `DEFAULT_DENY_NO_MATCH` |

## Invariants

### I1 — Determinism
For fixed inputs (c, P, x), D returns the same verdict, rule_id, reason_code, and trace.

**Proof sketch.** (i) R(P) extraction is deterministic or fails with a deterministic error code. (ii) Matching iterates in policy order only. (iii) Precedence is a total order with deterministic first-match selection. (iv) Trace is appended in a fixed sequence. Therefore outputs are identical for identical inputs.

### I2 — Default-Deny Safety
If policy is missing or invalid, verdict = deny with a stable reason_code.

**Proof sketch.** The resolver catches policy parse/validation failures and returns a deny decision with reason_code VALIDATION_DENY (or equivalent) without evaluating any allow branch. Therefore no capability is permitted on invalid input.

### I3 — Isolation Boundary (Non-Bypass)
Tools/plugins cannot bypass policy enforcement: any tool execution must pass through the tool gateway which invokes D.

**Proof sketch.** The only tool execution path is via the tool gateway entrypoint. The gateway requires a policy decision before tool invocation and enforces deny/approval/redaction outcomes. Under this control-flow constraint, a plugin cannot directly invoke tools without gateway mediation.
