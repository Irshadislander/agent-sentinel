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
