# Live Evaluation Notes

- `tab_live_eval_summary.tex` is the aggregate count-and-rate summary for the five-run OpenAI-backed live evaluation. It reports the total number of executions, task counts by class, attack blocking, model-side denials, and latency percentiles.
- `tab_live_eval_main_results.tex` is the paper-facing results table. It highlights the primary safety claims and keeps the presentation compact for the Evaluation section.
- `tab_live_eval_stability.tex` reports mean $\pm$ std across the five runs so the manuscript can discuss run-to-run stability instead of a single point estimate.
- `tab_live_attack_breakdown.tex` summarizes the attack-only slice by category, showing total cases, total denials, explicit Sentinel blocks, and the resulting blocked rate.
- `fig_live_eval_outcomes.png` visualizes the aggregate outcome composition by task type.
- `fig_live_eval_latency_boxplot.png` shows the latency distribution by task type.
