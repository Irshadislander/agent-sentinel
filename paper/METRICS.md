# Metrics Definitions

## Core Metrics

### 1) Unsafe Execution Rate (UER)
\[
\mathrm{UER} = \frac{\#(\text{denied-but-executed})}{\#(\text{denied requests})}
\]
Target under this system: \( \mathrm{UER} = 0 \).

### 2) Failure Ambiguity Rate (FAR)
\[
\mathrm{FAR} = \frac{\#(\text{failures with non-structured/unknown reason})}{\#(\text{failures})}
\]
Lower is better; ideal is 0.

### 3) Trace Completeness Ratio (TCR)
\[
\mathrm{TCR} = \frac{\#(\text{requests with trace event})}{\#(\text{requests})}
\]
Target: \( \mathrm{TCR} = 1 \).

### 4) Exit Determinism Score (EDS)
EDS quantifies stability of exit code class across repeated runs for equivalent request classes.
\[
\mathrm{EDS} = \frac{\#(\text{request classes with consistent exit class})}{\#(\text{request classes})}
\]
Target: \( \mathrm{EDS} = 1 \).

### 5) Policy Enforcement Accuracy (PEA)
\[
\mathrm{PEA} = \frac{\#(\text{correct allow/deny decisions})}{\#(\text{total decisions})}
\]
Requires labeled tasks with expected decision outcomes.

## Experimental Protocol
- Use a fixed benchmark task set (benign + malicious).
- Execute repeated runs per condition (e.g., 30 repetitions).
- Report mean and standard deviation for rate and latency-adjacent metrics.
- Preserve run metadata (timestamp, commit SHA, mode flags) for reproducibility.
