# Formal Capability Execution Model

## 1. Formal Objects
Let \(C\) be the capability space, where each \(c \in C\) is a canonical capability identifier.
Let \(X\) be the request-context space, where \(x \in X\) contains request metadata.
A policy is \(P = (R, \delta)\), where \(R = \langle r_1, \dots, r_n \rangle\) is a finite ordered rule sequence and \(\delta\) is the fallback action.
Each rule is a tuple \(r_i = (\varphi_i, a_i, \mathrm{id}_i)\), where \(\varphi_i: C \times X \to \{0,1\}\), \(a_i \in \{\mathrm{allow}, \mathrm{deny}\}\), and \(\mathrm{id}_i\) is a unique rule identifier.
Define rule matching set \(M(c, x, P) = \{i \in \{1,\dots,n\} \mid \varphi_i(c, x) = 1\}\).
Define first-match index \(i^*(c, x, P) = \min M(c, x, P)\) when \(M\neq\varnothing\).
Define deterministic decision function
\[
D(c, P, x) \to (d, \rho, \kappa),
\]
where \(d \in \{\mathrm{allow},\mathrm{deny}\}\), \(\rho \in \{\mathrm{id}_1,\dots,\mathrm{id}_n,\bot\}\), and \(\kappa\) is a reason code.
If \(P\) is invalid (including \(R=\varnothing\)), then \(D(c,P,x)=(\mathrm{deny},\bot,\mathrm{POLICY\_INVALID})\).
If \(P\) is valid and \(M=\varnothing\), then \(D(c,P,x)=(\mathrm{deny},\bot,\mathrm{NO\_RULE\_MATCH})\) (default-deny fallback).
If \(P\) is valid and \(M\neq\varnothing\), then \(D(c,P,x)=(a_{i^*},\mathrm{id}_{i^*},\mathrm{RULE\_MATCH})\).

## 2. Decision Semantics
Given \((c,P,x)\), evaluate \(D\) as follows:
1. Validate policy structure and rule ordering constraints.
2. If validation fails, return \((\mathrm{deny},\bot,\mathrm{POLICY\_INVALID})\).
3. For \(i=1\) to \(n\), evaluate \(\varphi_i(c,x)\).
4. At the first index with value \(1\), return \((a_i,\mathrm{id}_i,\mathrm{RULE\_MATCH})\).
5. If no rule matches, return \((\mathrm{deny},\bot,\mathrm{NO\_RULE\_MATCH})\).
The ordering over rules is total because \(R\) is a sequence.
The procedure is deterministic because each branch is selected by total-order iteration and predicate outcomes over fixed inputs.

## 3. Invariants
### Invariant 1 (Determinism)
For fixed \((c,P,x)\), \(D\) returns a unique tuple.
Formally,
\[
\forall c,P,x:\; D(c,P,x)=y_1 \land D(c,P,x)=y_2 \implies y_1=y_2.
\]

### Invariant 2 (Default-Deny Safety)
If policy is empty or invalid, denial is mandatory with policy-invalid reason code.
Formally,
\[
\forall c,x:\; \mathrm{Invalid}(P) \implies D(c,P,x)=(\mathrm{deny},\bot,\mathrm{POLICY\_INVALID}).
\]

### Invariant 3 (Plugin Isolation Boundary)
Capability invocation is reachable only through an allow outcome from \(D\).
Formally, for any plugin-mediated execution event \(\mathrm{Invoke}(c,x)\),
\[
\mathrm{Invoke}(c,x) \implies \exists \rho,\kappa:\; D(c,P,x)=(\mathrm{allow},\rho,\kappa).
\]

## 4. Proof Sketches
### Proof Sketch for Invariant 1 (Determinism)
1. Fix arbitrary \((c,P,x)\).
2. If \(P\) is invalid, the algorithm returns a constant terminal tuple by Step 2.
3. Otherwise, \(R\) is a finite ordered sequence with fixed index order.
4. Each predicate \(\varphi_i(c,x)\) is evaluated on fixed inputs, so each truth value is fixed.
5. If at least one predicate is true, the minimum true index \(i^*\) is unique by total order.
6. The returned tuple is uniquely determined by \(a_{i^*}\), \(\mathrm{id}_{i^*}\), and \(\mathrm{RULE\_MATCH}\).
7. If no predicate is true, the algorithm returns the unique default tuple \((\mathrm{deny},\bot,\mathrm{NO\_RULE\_MATCH})\).
8. Therefore the output tuple is unique for fixed \((c,P,x)\).

### Proof Sketch for Invariant 2 (Default-Deny Safety)
1. Assume \(\mathrm{Invalid}(P)\), including empty rule set.
2. Decision semantics Step 1 performs policy validation before rule evaluation.
3. Under the assumption, validation fails deterministically.
4. Step 2 is therefore the only reachable terminal branch.
5. Step 2 returns \((\mathrm{deny},\bot,\mathrm{POLICY\_INVALID})\) by definition.
6. No rule-evaluation branch is reachable under invalid policy.
7. No allow output can be produced in this execution path.
8. Hence invalid or empty policy implies mandatory deny with \(\mathrm{POLICY\_INVALID}\).

### Proof Sketch for Invariant 3 (Plugin Isolation Boundary)
1. Define execution relation with states: request-received, decision-resolved, capability-invoked.
2. Transition to decision-resolved is defined as evaluation of \(D(c,P,x)\).
3. Transition to capability-invoked is enabled only when decision component equals \(\mathrm{allow}\).
4. If decision is \(\mathrm{deny}\), the transition system terminates without invocation.
5. Plugin-mediated invocation is a subset of capability-invoked transitions.
6. Therefore any invocation implies existence of a prior decision-resolved state.
7. The enabling condition enforces decision \(=\mathrm{allow}\) for that prior state.
8. Hence plugin invocation cannot bypass \(D\); invocation implies an allow output from \(D\).
