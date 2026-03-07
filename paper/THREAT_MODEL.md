# Threat Model

## Attacker Capabilities
The attacker is assumed able to:

- manipulate prompts and external input content,
- attempt tool misuse (filesystem/network/shell requests),
- chain tool calls across multiple steps to reach unsafe effects,
- exploit capability requests by asking for actions beyond granted privileges.

## Attacker Goals
Primary attacker goals are:

- unauthorized tool execution,
- capability escalation from benign to privileged actions,
- data exfiltration via local reads or network output,
- reduced observability of malicious actions.

## System Trust Assumptions
This model assumes the enforcement core and policy store are controlled by trusted operators.
Security claims are runtime enforcement claims under these assumptions.

## Trusted Components
- runtime enforcement layer (tool gateway and decision path),
- policy evaluation logic and capability mapping,
- policy configuration under trusted administration,
- structured decision/trace emission path.

## Untrusted Components
- prompts and user-provided instructions,
- model-generated plans and tool arguments,
- external content returned to the agent,
- third-party tool/plugin behavior unless explicitly trusted.

## Explicit Non-Capabilities of the Attacker (In-Model)
Within this threat model, the attacker cannot:

- modify the enforcement layer implementation,
- modify policy configuration in trusted storage,
- bypass runtime decision evaluation before tool execution.

## Security Objectives
- enforce least privilege through capability gating and default deny,
- block unauthorized capability requests before side effects,
- preserve explainable decision artifacts (`decision`, `rule_id`, `reason_code`, trace metadata).

## Out of Scope
- compromised host/runtime trusted computing base,
- privileged tampering with enforcement code or policy storage,
- full OS/kernel compromise or equivalent infrastructure takeover.
