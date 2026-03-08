# Day 12 Results Summary

## Key Deltas (mean ± std)

### scale_n200
- no_plugin_isolation: ΔUER=+0.0000, ΔFAR=+0.0000, ΔTCR=+0.0000, ΔEDS=+0.0000
- no_policy: ΔUER=+1.0000, ΔFAR=+0.0000, ΔTCR=+0.0000, ΔEDS=+0.0000
- no_trace: ΔUER=+0.0000, ΔFAR=+0.0000, ΔTCR=-1.0000, ΔEDS=+0.0000
- raw_errors: ΔUER=+0.0000, ΔFAR=+1.0000, ΔTCR=+0.0000, ΔEDS=+0.0000

## Attack Success Rate (ASR) Interpretation

Low ASR indicates stronger runtime enforcement: fewer attack-labeled requests successfully cross the policy-gated tool boundary. Under fixed workload slices, ASR reductions should be interpreted as tighter capability mediation rather than changes in task mix.

The current Day 12 export is aggregate and reports system-level attack success outcomes. In the benchmark taxonomy, the hardest families to stop are typically multi-step privilege-abuse paths (for example `shell_misuse`, `data_exfiltration`, and `network_exfiltration` in harder scenarios) because they chain capabilities across steps. Family-level ASR values should be read from the appendix breakdown tables populated from the same matrix outputs.

## Production Agent Relevance
These Day 12 results come from benchmark scenarios, not from production deployment claims. The evaluated control path (request generation -> capability mediation -> allow/deny decision -> trace artifact) is, however, the same control point used by LangChain-style tool agents, OpenAI tool-calling runtimes, and multi-agent orchestration systems.

Accordingly, results should be interpreted as framework-relevant evidence of runtime enforcement behavior under controlled workloads, with production-framework evaluation left as future work.

## Real Agent Evaluation Summary
The real-agent case study (`examples/agent_integration/run_case_study.py`) shows the mediation loop on concrete tool requests rather than metric-only aggregates. Each case executes request construction, gateway mediation, allow/deny decision, and trace artifact emission.

Observed behavior is consistent with policy intent:
- mediated safe actions are allowed under restrictive policies when required capabilities are granted,
- attack-style shell requests are blocked when shell capability is denied,
- permissive-policy control cases allow shell execution by design.
