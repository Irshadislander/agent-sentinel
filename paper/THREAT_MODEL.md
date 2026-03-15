# Threat Model

## Threat Boundaries
Agent-Sentinel is designed for tool-using LLM agents that can access external execution surfaces such as filesystem, network, and shell interfaces. The attacker is modeled as controlling or influencing inputs to the agent and attempting to induce unsafe tool use at runtime.

### In-Scope Threats
The attacker can:

- perform prompt injection attacks through user input, retrieved content, or intermediate context;
- induce malicious tool request generation, including unsafe arguments and unauthorized actions;
- attempt capability escalation through chained tool invocations;
- attempt data exfiltration through tool outputs, including cross-tool flows;
- embed adversarial instructions or payloads in tool outputs that influence later tool calls.

### Out-of-Scope Threats
The attacker cannot:

- modify the agent runtime code;
- modify policy files or trusted policy state;
- compromise the OS kernel;
- perform hardware attacks;
- exploit side channels against the gateway mediation path;
- directly invoke tools outside the gateway.

## Trusted Computing Base (TCB)
The following components are trusted:

- **Tool Gateway:** intercepts all tool requests before execution;
- **Policy Engine:** evaluates capability policies and returns allow/deny decisions;
- **Validators:** perform argument-level safety checks on mediated requests;
- **Audit Trail:** records immutable decision and execution evidence;
- **Policy Configuration:** defines capability mappings and ordered policy rules under trusted administration.

The gateway mediation layer is assumed to be always interposed between the agent and all external tools.

Security claims in this paper are conditioned on this TCB remaining intact and correctly configured.

## Untrusted Components
The following components are treated as adversarial or potentially adversarial:

- the LLM agent itself;
- tool outputs;
- external APIs;
- file system inputs;
- network responses.

Agent-Sentinel therefore treats the agent as potentially compromised via prompt injection. Model-generated plans, tool selections, and tool arguments are not trusted inputs to the enforcement decision.

## Attack Surface
The core attack interface is:

`LLM agent -> tool invocation -> system resources`

Within this interface, the primary attack surfaces are:

- **tool arguments:** malicious parameters, path targets, command payloads, and exfiltration destinations;
- **chained tool invocation:** multi-step sequences that transfer authority or data across tools;
- **external API responses:** attacker-controlled or attacker-influenced content returned to the agent;
- **file access requests:** reads or writes that expose sensitive state or stage later actions.

This threat model focuses on attacks that attempt to cross the tool boundary and produce unauthorized side effects on external resources.

## Security Goals
Within the stated assumptions, Agent-Sentinel aims to provide:

- **Capability Confinement:** requests requiring ungranted capabilities are denied before tool execution;
- **Policy Enforcement:** each tool request is mediated by policy at runtime with explicit allow/deny semantics;
- **Auditability:** decisions and relevant execution metadata are recorded for post-hoc analysis;
- **Controlled Tool Invocation:** tool access is constrained to authorized calls that pass gateway mediation and validation.

These are runtime mediation guarantees for the tool boundary. They are not claims of full system security or formal verification of the complete deployment.

## Non-Goals
Agent-Sentinel does not defend against:

- malicious tool implementations;
- OS compromise;
- policy misconfiguration.

It is a runtime mediation layer, not a complete substitute for secure tool design, system hardening, or policy review.
