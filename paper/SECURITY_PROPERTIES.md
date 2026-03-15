# Security Properties

Agent-Sentinel enforces runtime capability mediation for tool-using LLM agents. Within the threat model assumptions defined earlier, we describe two core properties.

## Property 1: Capability Confinement

### Definition
If a tool invocation requires capability `C` and `C` is not granted to the agent under the current policy, then the invocation is denied before tool execution.

### Formal Statement
For any tool request `R` requiring capability `C`:

`policy(agent, C) = DENY -> tool execution is not performed`

### Proof Sketch
1. The agent generates a tool request `R`.
2. The request is intercepted by the Tool Gateway before execution.
3. The gateway forwards the request to the Policy Engine.
4. The Policy Engine evaluates the capability requirements for tool `T`.
5. If capability `C` is denied, the decision engine returns `DENY`.
6. The tool invocation is not forwarded to the execution layer.

Because all tool invocations pass through the gateway mediation path, there is no execution path that bypasses this check.

### Assumptions
- gateway mediation is always interposed;
- tools cannot be invoked directly by the agent runtime;
- policy engine evaluation is deterministic.

## Property 2: Capability Non-Interference

### Definition
Policy rules governing capability `C1` do not affect enforcement behavior for capability `C2` when `C1 != C2`.

### Proof Sketch
1. Policies are evaluated independently for each capability.
2. The policy engine computes decisions as `policy(agent, capability) -> {ALLOW, DENY}`.
3. Capability checks are performed per request based on the capabilities required by that request.
4. Decisions for capability `C1` do not modify the evaluation logic for capability `C2`.

Therefore, under capability-independent policy design, policies do not interfere across capabilities.

## Validation

We empirically validated these properties through the adversarial evaluation suite described in the evaluation section, where policies for multiple capabilities were varied independently across attack scenarios.

These are scoped enforcement claims about the mediated runtime boundary. They are not claims of full system security or machine-checked formal verification.
