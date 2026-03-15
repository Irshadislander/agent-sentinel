# Related Work

Agent-Sentinel sits at the intersection of LLM-agent security, policy enforcement, and tool-calling infrastructure. Relative to recent work, its contribution is not a new agent framework or a benchmark-first platform, but a runtime mediation layer for tool execution with an explicit capability model, bounded formal claims, and auditable enforcement outputs.

## Capability Control for LLM Agents
Progent studies programmable privilege control for LLM agents. Its central contribution is a domain-specific language for writing privilege policies over tool calls, enabling flexible and programmable control logic. This is useful for expressing rich policies and adapting them to different tool-use contexts.

Agent-Sentinel is positioned differently. It centers an explicit capability-based security model, a runtime mediation gateway that interposes before execution, a scoped capability-confinement property, and structured audit artifacts that support post-hoc forensic analysis. In reviewer-facing terms, Progent emphasizes **policy programmability**, whereas Agent-Sentinel emphasizes **runtime capability mediation and enforcement guarantees**.

## Agent Security Benchmarks
SafeAgentBench and Agent Security Bench (ASB) represent a benchmark-oriented line of work for evaluating LLM agents under adversarial or safety-critical conditions. These efforts prioritize broad coverage of attack settings, standardized evaluation, and large test surfaces. ASB in particular spans hundreds of tools, while this benchmark line more generally emphasizes many attack scenarios and systematic comparison across agents or defenses.

Agent-Sentinel is not primarily a benchmark contribution. Its primary contribution is a runtime mediation architecture with explicit capability enforcement. The evaluation is therefore narrower and mechanism-focused: a targeted adversarial study using 75 attack scenarios to assess how the mediation layer performs at the tool boundary.

## Tool Framework Security
LangChain tool calling, OpenAI function calling, and Model Context Protocol (MCP) provide the interfaces by which LLMs invoke external tools or services. These frameworks are important operational substrates for agent systems, but they do not by themselves enforce capability restrictions, argument-level policy checks, or runtime mediation guarantees at execution time.

Agent-Sentinel is designed as a security layer above such frameworks. It treats tool-calling infrastructure as the integration point at which capability boundaries should be enforced, so that tool requests are checked before they reach filesystem, network, shell, or plugin execution paths.

## Comparison Table

| System | Runtime Tool Mediation | Capability Model | Audit Trail | Formal Security Properties | Evaluation |
|---|---|---|---|---|---|
| Progent | Partial | Programmable privilege rules / DSL | Limited | No | System evaluation |
| SafeAgentBench | No | No explicit capability model | No | No | Benchmark evaluation |
| Agent Security Bench | No | No explicit capability model | No | No | Large-scale adversarial benchmark |
| LangChain / MCP | No | No built-in capability restrictions | Partial | No | Infrastructure, not security evaluation |
| **Agent-Sentinel** | **✓** | **✓ explicit capability model** | **✓ structured audit trail** | **✓ scoped formal properties** | **✓ adversarial evaluation** |
