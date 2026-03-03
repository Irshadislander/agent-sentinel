# Threat Model

## Assets
- Protected resources accessed by tools (filesystem, network, secrets, external APIs).
- Integrity of policy decisions (verdict + reason_code + rule_id).
- Audit integrity: completeness and correctness of traces and emitted audit events.

## Trust boundaries
- **Trusted:** policy engine core + tool gateway enforcement + audit emitter.
- **Untrusted:** agent prompts, tool arguments, external content, and third-party plugins.
- **Partially trusted:** policy documents (may be malformed, missing, or attacker-supplied).

## Adversary capabilities
- Prompt injection to induce tool misuse.
- Attempted capability escalation (e.g., ask for fs.write when only fs.read allowed).
- Attempted trace suppression or output manipulation (tamper, truncate, omit).
- Malicious plugin attempting direct tool calls or bypassing intended flow.

## Out of scope
- OS kernel compromise / full host takeover.
- Side-channel leakage (timing/power) beyond coarse latency metrics.
- Network MITM outside the agent runtime boundary.

## Security goals
- Enforce least privilege: deny by default, allow only explicitly permitted capabilities.
- Produce stable explanations: deterministic reason codes and matched rule identifiers.
- Produce auditable traces: events sufficient to reconstruct “why” and “what happened”.
