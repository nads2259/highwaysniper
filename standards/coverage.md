# Spec coverage

Honest map of what you specified versus what shipped. The agentic layer does not replace software engineering; it makes the deterministic skeleton more important.

## Included (in `standards/` + `agent_kernel` + package layout)

| Area | Where |
| --- | --- |
| Goal processor loop, deterministic shell vs agentic points | `standards/future-surviving-agent.md` |
| Lifecycle state machine + illegal transitions | `agent_kernel/lifecycle.py` |
| Task / result / plan DAG / events / manifest / RuntimeBundle | `agent_kernel/contracts/` |
| Failure *categories* | `FailureCategory` |
| Four validation levels, memory kinds, agent-vs-OS ownership | standard markdown |
| Package tree (nodes, ports, adapters, eval families) | `templates/agent/`, `agents/prompts_specialist/` |
| Canonical protocol names, adapter *list* | `agent_kernel/protocol.py` |
| Terminal statuses including partial/blocked/denied | `TerminalStatus` |

## Missing or only named, now being filled

| Gap | Why it mattered |
| --- | --- |
| SOLID ports (`ChatModelPort`, `ToolExecutionPort`, …) | Provider SDKs could leak into nodes |
| Adapter conformance suite | LSP / “provider-neutral” was theoretical |
| Typed `AgentError` tree + serializable `FailureEnvelope` | Failures were an enum, not a decision contract |
| Error decision matrix (retry vs replan vs stop) | One retry loop would return |
| `TaskLease`, fencing token, `BudgetEnvelope` | Concurrency and economics were prose |
| Delegated authority, evidence/checkpoint/memory records as types | Named in the standard, not coded |
| Hierarchical RuntimeBundle fields (prompt hashes, sandbox profile) | Partial YAML only |
| Context compiler as a port, not prompt concat | Still a stub node |
| Tool supply-chain descriptor | Not a type |
| `Agent` type + **per-run instance** (`spawn`) | No concurrent/async execution model |
| Async nodes + isolated instance state | Sync functions, easy to share mutable state |
| Engineering rules (no BaseAgent hierarchy, functional nodes) | Not written down |
| Eval OS, release pipeline, SLOs, self-improvement, Postgres/Redis/OTel wiring | Still **standard-only** — platform Agent OS, not faked inside each agent |

## Still not a production Agent OS (intentionally)

Durable Postgres checkpointers, Redis Streams workers, object storage, append-only ledger backends, OpenTelemetry exporters, signed releases, canary, and AGNTCY identity **belong to the platform**. Agents depend on ports. Shipping fake infrastructure inside every package would violate hexagonal design.

This change adds the **deterministic skeleton and instance model**. Platform adapters remain replaceable.
