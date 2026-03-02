# Related Work (Structured Buckets)

## 1. Capability and Access-Control Models

- Capability-based security and least-privilege models motivate explicit permission boundaries.
- This project adapts those ideas to tool-using agent runtimes with request-level enforcement and baseline ablations.

## 2. Policy Enforcement and Runtime Sandboxing

- Existing systems focus on static policy checks, container isolation, or API gateways.
- The presented approach emphasizes per-tool call enforcement with measurable decision outcomes and policy-sensitive error taxonomy.

## 3. Audit Logging and Forensic Traceability

- Traditional audit systems prioritize event collection and retention.
- Here, trace completeness is elevated to a measurable invariant (TCR), directly tied to baseline controls.

## 4. Agent Safety and Prompt-Injection Defenses

- Prior defenses often focus on prompt filtering or model-side heuristics.
- This work centers runtime control at the execution boundary, where policy, trace, and deterministic error semantics can be evaluated empirically.

## 5. Benchmarking and Reproducibility Practices

- Many evaluations provide aggregate metrics without mechanism-level ablations.
- The matrix baseline design plus reproducibility script connects implementation controls to paper-ready quantitative claims.
