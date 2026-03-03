# Related Work

## Comparative Table

| System / Work | Runtime Gating | Plugin Isolation | Trace Completeness Metric | Causal Ablations | Reproducible Harness |
|---|---|---|---|---|---|
| OPA (Open Policy Agent) | partial | ✗ | ✗ | ✗ | partial |
| Traditional RBAC systems | partial | ✗ | ✗ | ✗ | ✗ |
| API Gateway enforcement | ✓ | ✗ | partial | ✗ | partial |
| WASM sandboxing | partial | ✓ | ✗ | ✗ | partial |
| Capability-based OS models | ✓ | partial | ✗ | ✗ | ✗ |
| Agent wrapper systems (generic) | partial | partial | partial | ✗ | partial |
| Agent-Sentinel | ✓ | ✓ | ✓ | ✓ | ✓ |

Notes on conservative labeling:
- `partial` denotes support that exists but is not the primary abstraction for tool-level agent-runtime safety evaluation.
- Table entries reflect general system classes, not claims about every implementation variant.

## Gap Analysis

Existing approaches provide important building blocks: OPA and RBAC provide policy expression and authorization structure; API gateways provide operational request mediation; sandboxing provides strong isolation boundaries; capability-based models provide principled least-privilege semantics; and agent wrappers provide practical orchestration hooks. However, these lines of work typically do not provide a unified method to causally evaluate runtime safety controls for tool-augmented agents under controlled ablations with explicit safety and observability metrics. The missing niche is not only enforcement, but measurement of enforcement effects: whether policy gating changes unsafe execution, whether trace controls change completeness, and whether error typing changes ambiguity under adversarial tasks. This is why the contribution is not merely an access-control wrapper: the evaluation methodology (baseline matrix, adversarial task design, and reproducible harness outputs) is a first-class research object alongside the control mechanism.

## Positioning

We differ from prior work in that we formalize deterministic decision semantics at the capability boundary, quantify safety-observability-latency tradeoffs with explicit metrics, evaluate control layers through controlled ablations, and release a reproducible harness that ties runtime behavior to paper-level claims.
