# Figures

This file defines publication-oriented figure specifications for paper-ready outputs.

## Figure 1: Agent-Sentinel System Architecture Overview
- **Title**: Agent-Sentinel System Architecture Overview
- **Purpose**: present the end-to-end runtime mediation path for tool-using agents.
- **Architecture components**:
  - User / Task Input
  - LLM Agent
  - Tool Request
  - Agent-Sentinel Runtime Gateway
  - Policy Engine
  - Capability Check
  - Allow / Deny Decision
  - Tool Execution Layer
  - Trace / Audit Output
- **Reviewer should learn**: authorization is enforced at runtime before tool side effects, with explicit policy/capability checks and auditable outputs.
- **Expected output filename**: `paper/figures/fig_architecture_overview.png`

## Figure 2: Attack Family Blocking Summary
- **Title**: Attack Family Blocking Summary
- **Purpose**: compare security outcomes across attack families under baseline and reference conditions.
- **Reviewer should learn**: which attack families are more effectively blocked and where failure pressure concentrates.
- **Expected output filename**: `paper/figures/fig_attack_family_blocking_summary.png`

## Figure 3: Baseline Comparison Figure
- **Title**: Baseline Comparison (Mean ± Std)
- **Purpose**: provide a compact cross-baseline comparison of primary security/trace metrics.
- **Reviewer should learn**: how Agent-Sentinel compares to weaker or ablated baseline conditions.
- **Expected output filename**: `paper/figures/fig_baselines_mean_std.png`

## Figure 4: Trace Tradeoff Figure
- **Title**: Trace Tradeoff
- **Purpose**: show observability behavior as trace sampling changes.
- **Reviewer should learn**: trace coverage tradeoffs are measurable and separable from enforcement semantics.
- **Expected output filename**: `paper/figures/fig_trace_tradeoff.png`

## Figure 5: Latency Tradeoff Figure
- **Title**: Latency Tradeoff
- **Purpose**: summarize runtime overhead relative to security outcomes.
- **Reviewer should learn**: latency impact can be assessed together with security effectiveness in a single view.
- **Expected output filename**: `paper/figures/fig_latency_tradeoff.png`
