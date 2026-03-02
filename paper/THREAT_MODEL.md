# Threat Model

## Attacker Model

- The attacker controls or influences task inputs, prompts, payload fields, and tool-call intents.
- The attacker may attempt:
  - policy bypass (`no_policy`-like behavior),
  - exfiltration via network-capable tools,
  - malformed payload injection to induce ambiguous failures,
  - plugin misuse or contract violation in extension surfaces.

## Trust Assumptions

- Runtime enforcement code and benchmark harness are trusted.
- Policy files are trusted inputs once validated.
- Host filesystem and process isolation are assumed baseline-secure for local execution.
- Tool implementations may fail and are treated as untrusted from a contract perspective.

## Security Guarantees (Target)

- **G1 Non-bypassability**: a denied request does not execute in enforced mode.
- **G2 Deterministic failure classes**: structured policy/runtime failures map to stable error kinds and exit semantics.
- **G3 Traceability**: traced mode records complete request outcomes for downstream audit/metrics.
- **G4 Baseline detectability**: removing a control (`no_policy`, `no_trace`, `raw_errors`) produces measurable metric degradation.

## Failure Modes

- Policy misconfiguration permits unintended capabilities.
- Disabling trace (`no_trace`) reduces forensic completeness (TCR drops).
- Raw exception paths (`raw_errors`) increase ambiguity (FAR rises).
- Unsafe plugin loading increases contract-violation surface and runtime instability.
