# Limitations

## Security Scope Limits
- Agent-Sentinel is **not a full sandbox**; it is a runtime capability-gating and audit layer.
- It does not replace host/container isolation controls.

## Policy Dependence
- The system assumes **correct policy configuration**.
- Misconfigured or over-permissive policies can still allow unsafe behavior.

## Trusted Runtime Assumptions
- The approach cannot defend against a **compromised runtime environment** (for example, tampered enforcement core or policy store).
- If trusted components are compromised, enforcement guarantees no longer hold.

## Evaluation Coverage Limits
- Evaluation is limited to the defined attack families and workload sets.
- Results do not claim coverage of all real-world attack strategies.
- Performance and robustness outcomes remain deployment/environment dependent.

## Methodological Scope
- This work addresses runtime authorization and decision observability.
- It does not claim complete end-to-end AI security, model alignment, or infrastructure hardening.

## Links
- [THREAT_MODEL](THREAT_MODEL.md)
- [ATTACK_SCENARIOS](ATTACK_SCENARIOS.md)
- [EVAL_PROTOCOL](EVAL_PROTOCOL.md)
