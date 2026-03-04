# Formal Properties

## Safety Monotonicity (Theorem)

If deny constraints are strengthened, the allowed capability set cannot increase.

### Definitions
Let the request universe be a fixed finite set of capabilities \(U \subseteq \mathcal{C}\) under a fixed context \(x\).

For policy \(P\), let:
\[
\mathrm{Allowed}(P) = \{ c \in U \mid D(c, P, x).\mathrm{decision} = \texttt{allow} \}
\]
\[
\mathrm{Deny}(P) = U \setminus \mathrm{Allowed}(P)
\]

`Allowed(P)` is defined by the deterministic resolver \(D\) in [FORMAL_MODEL](FORMAL_MODEL.md): each request maps to exactly one terminal decision (`allow` or `deny`) via first-match resolution with default deny fallback.

### Property Statement
If:
\[
\mathrm{Deny}(P') \supseteq \mathrm{Deny}(P)
\]
then:
\[
\mathrm{Allowed}(P') \subseteq \mathrm{Allowed}(P)
\]

### Proof Sketch
1. The resolver is deterministic and total on \(U\): each request ends in exactly one of `allow` or `deny` (first-match rule or default deny).
2. Therefore \(\mathrm{Allowed}(P)\) and \(\mathrm{Deny}(P)\) are complementary over the same universe \(U\).
3. Assume \(\mathrm{Deny}(P') \supseteq \mathrm{Deny}(P)\). Taking complements in \(U\) yields:
   \[
   U \setminus \mathrm{Deny}(P') \subseteq U \setminus \mathrm{Deny}(P)
   \]
4. By definition, \(U \setminus \mathrm{Deny}(P) = \mathrm{Allowed}(P)\), so:
   \[
   \mathrm{Allowed}(P') \subseteq \mathrm{Allowed}(P)
   \]
5. In this implementation, deny precedence is enforced by ordered first-match semantics: adding earlier deny rules can only preserve or shrink the allow set; default deny prevents uncontrolled expansion.

### Implications
- Tightening policy cannot accidentally open new capabilities.
- Security reviewers can reason monotonically about policy hardening steps.
- CI checks can assert that added deny rules never increase `Allowed(P)` for a fixed request universe.
