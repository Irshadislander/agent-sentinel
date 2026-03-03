# Niche

Agent-Sentinel studies **causal evaluation of runtime safety controls for tool-augmented agents** (policy gating + plugin/tool gateway enforcement + audit trace completeness) via a **reproducible ablation harness**.

## Why important
- Tool-using agents are becoming production systems; safety failures are operational incidents, not theoretical.
- Existing “guardrails” are often evaluated qualitatively; we need measurable, reproducible, causal evidence.

## Why hard
- Safety controls interact (policy + gateway + audit + redactions); naive evaluation confounds effects.
- Adversarial prompts and tool misuse create high-variance failure modes.

## Why now
- Tool-enabled agent stacks are shipping widely, but evaluation standards for runtime controls are not yet mature.
