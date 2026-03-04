# Metrics

## Safety metrics

- **Policy decision correctness (%)**: fraction of decisions matching expected test-case outcomes.
- **Unsafe Execution Rate (UER)**:
  \[
  \mathrm{UER}=\frac{\#(\text{expected deny but allowed})}{\#(\text{expected deny})}
  \]
  Lower is better (ideal: \(0\)).
- **Attack success rate (%)**: fraction of attack-category tasks that reach an allow/success outcome.
  Lower is better.

## Observability metrics

- **Trace Completeness Rate (TCR)**:
  \[
  \mathrm{TCR}=\frac{\#(\text{requests with trace evidence})}{\#(\text{requests})}
  \]
  Higher is better (ideal: \(1\)).
- **Reason-code coverage (%)**: fraction of deny outcomes with non-empty, non-unknown reason codes.
  Higher is better.
- **Trace integrity detectability**: proportion of tamper scenarios where mismatch is detected.
  Higher is better.

## Performance metrics (p50/p95/p99)

- **Decision latency distribution** in ms from runtime decision paths:
  - \(p50\): median latency
  - \(p95\): tail latency
  - \(p99\): extreme tail latency
- **Stress scaling curve**: \(p95\) under increasing policy rule counts.
- **Overhead deltas**: latency delta versus baseline configuration.

## Explainability metrics (% with rule_id)

- **Rule-ID coverage (%)**:
  \[
  \frac{\#(\text{decisions with rule\_id present})}{\#(\text{decisions})}
  \]
  Higher is better.
- **Deterministic explanation stability (%)**: repeated fixed-input runs producing the same
  `(verdict, rule_id, reason_code, trace class)`.
