# Robustness Evaluation

This section reports attack-oriented checks for runtime policy enforcement, decision explainability, and traceability. The objective is to verify that bypass attempts fail with explicit reason codes and observable trace signatures.

## Attack Scenario Mapping

| Attack scenario | Expected outcome | Expected reason_code | Expected trace signature |
|---|---|---|---|
| Policy bypass attempt (request disallowed capability) | Deny | `DEFAULT_DENY_NO_MATCH` or `RULE_DENY_MATCH` | contains `no_match` or `match:<rule_id>:deny` and terminal `final:deny:<reason_code>` |
| Plugin override attempt (tool-name alias spoofing) | Deny under insufficient capabilities | capability-specific deny path (`RULE_DENY_MATCH`/default-deny equivalent) | normalized evaluation path with deterministic terminal deny trace |
| Trace suppression attempt (malformed context/policy input) | Deny for invalid/missing policy, trace still emitted | `POLICY_INVALID` or `POLICY_MISSING` | includes `policy:invalid` or `policy:missing` and terminal deny trace |

## Robustness Metrics in Reports

- Denial reason distribution: count denials by `reason_code`.
- Category-level concentration: top denial reason codes per task category.
- Critical safety check: `denied-but-executed` count, expected to remain `0` in secured mode.

These measurements are integrated into benchmark reporting to make denial causes auditable and comparable across baseline settings.

## Trace Integrity & Tamper Evidence

When `trace_integrity` is enabled in policy, each evaluation trace is committed via a deterministic hash chain:

- `h_0 = 0^256` (fixed zero seed)
- `h_i = H(h_{i-1} || trace_entry_i)`
- `trace_commitment = h_n`

The commitment is emitted in decision/audit outputs. This provides lightweight tamper evidence:

- Entry mutation changes `trace_commitment`.
- Trace truncation changes `trace_commitment`.
- Recomputed commitment mismatch indicates post-decision trace modification.

Integrity mode is optional to support overhead measurement; disabling it keeps prior behavior while preserving deterministic decision semantics.
