# Threat Model

## 1. Assets

The protected asset set consists of:
- Protected resources: filesystem reads/writes, outbound network calls, and system-tool invocations mediated through capabilities.
- Policy integrity: correctness and precedence order of the rule set used by the decision function.
- Trace integrity: completeness and consistency of emitted decision/exit evidence for each request.
- Plugin boundary integrity: constraints on capability extension points, including registration and invocation isolation.

A security failure occurs when protected resources are accessed against policy intent, when policy semantics are silently altered, or when trace evidence is absent/ambiguous under enforced mode.

## 2. Trust Boundaries

- Core engine (trusted): decision semantics, enforcement dispatch, and baseline harness control logic.
- Policy source (constrained trust): policy content is trusted only after schema/structure validation and rule-order interpretation.
- Plugins (untrusted by default): plugin code and metadata are untrusted unless explicitly allowlisted and isolated by registry rules.
- Agent/caller inputs (untrusted): prompts, payloads, capability requests, and context fields are attacker-influenced inputs.

Boundary crossings:
- Untrusted request inputs cross into the trusted decision boundary at evaluation time.
- Policy artifacts cross into trusted state only after validation.
- Plugin code crosses into execution path only after registry/allowlist gating.
- Trace outputs cross from trusted decision state to external observability artifacts.

## 3. Adversary Model

Attacker capabilities include:
- Prompt-injection attempts that induce disallowed capability requests.
- Malicious plugin registration or plugin metadata manipulation attempts.
- Capability misuse attempts (requesting over-privileged or policy-blocked actions).
- Crafted malformed inputs intended to trigger ambiguous or non-structured failures.
- Policy misconfiguration attempts (for example, inducing permissive rules or invalid policy states).

Attacker limitations:
- Cannot modify core engine binaries/interpreter runtime in-memory semantics.
- Cannot bypass the defined decision function path in enforced mode.
- Cannot assume privileged host/kernel compromise through this threat model.

## 4. Out of Scope

The following are explicitly out of scope:
- Kernel or hypervisor compromise.
- Arbitrary code execution inside trusted engine components.
- Physical access attacks on host hardware.
- Supply-chain compromise of dependencies, interpreters, or build artifacts.

## 5. Attack Scenarios

### Scenario A: Policy Bypass Attempt

- Goal: execute a capability that should be denied by policy.
- Attack path: attacker issues capability requests crafted to avoid rule predicates or exploit policy gaps.
- Expected failure point: decision boundary enforces first-match semantics with default-deny fallback; unmatched or invalid-policy states resolve to deny.
- Measured metric impact: in `default`, UER should remain near zero; in `no_policy`, UER is expected to increase and reveal bypass susceptibility.
- Baseline connection: primary contrast is `default` vs `no_policy`.

### Scenario B: Plugin Override Attempt

- Goal: register or execute an unsafe plugin capability that bypasses isolation constraints.
- Attack path: attacker introduces plugin entries that collide with expected capability behavior or bypass allowlist checks.
- Isolation enforcement behavior: plugin invocation is permitted only through registry-mediated enforcement; unallowlisted or invalid plugin paths are blocked in enforced mode.
- Metric effect: plugin-load and failure signatures should remain bounded under `default`; degradation is expected under `no_plugin_isolation` (higher unsafe execution/failure instability).
- Baseline connection: primary contrast is `default` vs `no_plugin_isolation`.

### Scenario C: Trace Suppression Attempt

- Goal: reduce forensic visibility by preventing trace emission for decision outcomes.
- Attack path: attacker induces paths that would benefit from missing trace artifacts (for example, ambiguous failure sequences).
- Observability degradation: suppressed tracing reduces request-to-event coverage and impairs post-hoc attribution.
- Latency/safety tradeoff: disabling trace may reduce runtime overhead while decreasing TCR; safety controls may remain active but become less auditable.
- Measured metric impact: TCR should drop under `no_trace`, with explicit comparison of latency percentiles against `default`.
- Baseline connection: primary contrast is `default` vs `no_trace`.
