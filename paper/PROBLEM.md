# Problem Definition

## Entities

- **Agent**: planner that proposes tool/capability requests from task context.
- **Capability**: named execution permission associated with a runtime action.
- **Policy**: allow/deny constraints over capabilities and request context.
- **Plugin**: extension surface that can supply or override capability behavior.
- **Trace**: structured event record emitted per request path.
- **Task**: benchmark workload composed of ordered tool-call steps.

## Trust Boundary

Trusted components:
- enforcement runtime (policy check path and decision logic),
- benchmark harness and metric computation,
- validated policy input format.

Untrusted or adversarial inputs:
- task payloads and planner-proposed tool arguments,
- prompt-derived instructions,
- plugin behavior at execution boundaries.

## Formal Objective

Given a fixed task distribution and policy constraints, optimize operational utility while minimizing unsafe execution and ambiguity:

- maximize benign task success,
- minimize unsafe execution under denied conditions,
- maximize trace completeness for forensic accountability,
- preserve deterministic error/exit semantics under repeated runs,
- constrain extension behavior under plugin isolation controls.

## Metric Mapping

- **UER**: unsafe execution under denied-required categories (`malicious`, `policy_blocked`).
- **FAR**: proportion of failures with ambiguous/non-structured error taxonomy.
- **TCR**: fraction of requests with emitted trace evidence.
- **EDS**: stability of exit-class outcomes across repeated request classes.
- **plugin_loads**: loaded plugin entrypoint count as an isolation/extension-surface indicator.
- **latency**: p50/p95 runtime overhead under each baseline mode.
