# Attack Scenarios

## S1 — Prompt-Injection Tool Escalation
- Goal: induce the agent to call a denied tool (e.g., fs.write or arbitrary http).
- Path: attacker content instructs the agent to “ignore policy” and exfiltrate secrets.
- Mitigation: tool gateway resolves capability against policy; denies with reason_code; no tool execution occurs.
- Residual risk: if capability is mistakenly allowed by policy authoring, enforcement cannot correct bad policy.

## S2 — Malicious Plugin Bypass Attempt
- Goal: a plugin attempts to execute tool actions without policy mediation.
- Path: plugin code tries to call tool execution entrypoint directly.
- Mitigation: isolation boundary requires gateway mediation; bypass path absent or blocked; audits capture attempt/denial.
- Residual risk: out-of-scope if attacker has arbitrary code execution in trusted core.

## S3 — Trace Suppression / Truncation
- Goal: avoid leaving evidence (omit decision reason or erase trace).
- Path: attacker attempts to suppress logs, truncate records, or modify emitted decision fields.
- Mitigation: trace integrity tests + canonical reporting asserts trace fields are produced; audit schema requires decision + reason_code + timing; tamper attempts are detectable in report validation.
- Residual risk: external log store compromise is out-of-scope; we can only guarantee emission, not external persistence.
