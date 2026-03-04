# Limitations

## Scope Boundaries
- The model targets runtime capability enforcement and audit behavior, not model alignment or secure prompt engineering end-to-end.
- Security guarantees depend on gateway mediation and trusted core runtime assumptions.

## Experimental Limits
- Synthetic and benchmark tasks may not capture all real-world workflow complexity.
- Performance numbers are environment-dependent and should be interpreted with configuration metadata.

## Threat Model Limits
- Kernel compromise, host takeover, and supply-chain compromise remain out of scope.
- External log-store tampering is only partially addressed by local trace-integrity evidence.

## Next Steps
Future work includes stronger external audit-store integrity guarantees, broader plugin adversary models, and cross-runtime evaluations.

## Links
- [FORMAL_MODEL](FORMAL_MODEL.md)
- [THREAT_MODEL](THREAT_MODEL.md)
- [METRICS](METRICS.md)
- [RESULTS](results_tables.md)
- [ROBUSTNESS](ROBUSTNESS.md)
- [PERF](PERF_DAYXX.md)
