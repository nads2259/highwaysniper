# Engineering the deterministic runtime

The agentic layer does not replace software engineering. It makes strong engineering more important because you are controlling probabilistic behaviour.

**SOLID and OOP structure the deterministic runtime.** They must not model every prompt or graph node as a class hierarchy.

```text
Production Agent =
    Domain contracts
  + SOLID component boundaries
  + Selective OOP
  + Functional transformations
  + Explicit state machine
  + Typed failure model
  + Distributed-system resilience
  + Agentic planning and reasoning
  + Independent validation
```

## Where principles apply

| Principle | Application |
| --- | --- |
| SOLID | Replaceable models, tools, stores, validators, schedulers |
| OOP | Long-lived components with identity, lifecycle, invariants |
| Functional design | Stateless graph nodes, transformations, validators |
| Design by contract | Task, result, capability, evidence schemas |
| State machines | Legal lifecycle transitions only |
| Hexagonal architecture | Provider SDKs stay in adapters |
| Error taxonomy | Retry, repair, replan, compensate, escalate |
| Resilience | Timeout, lease, bulkhead, saga, degradation |
| DDD | Domain reasoning vs platform infrastructure |

## Instance model (concurrency)

An **agent type** is reusable configuration (ports + domain nodes). A **run** is a new instance with isolated working state.

```text
100 concurrent executions = 100 instances
```

```python
agent = PromptsSpecialist(ports=ports)          # type / factory
run = agent.spawn()                             # one instance
result = await run.execute(task)

results = await asyncio.gather(
    *[agent.spawn().execute(task) for task in tasks]
)
```

Do not store run state on the agent type. Do not use a process-global model client with implicit config. Ports may be shared only if they are async-safe and hold no per-task mutable state.

## OOP vs functions

OOP: `Agent`, `AgentRun`, `TaskLease`, `RuntimeBundle`, `BudgetEnvelope`, `EvidenceLedger` port, registries, routers.

Functions: graph nodes (`async def validate_plan(state, validator) -> dict`).

Forbidden: `AbstractBaseNode → AgentNode → IntelligentAgentNode → PlanningIntelligentAgentNode`.

Forbidden: one `AgentService` that plans, calls models, executes tools, validates, retries, stores memory, and publishes events.

## Hexagonal layout

```text
Domain (goals, plans, validation, policies)
Application (use cases, orchestration, transitions)
Ports (model, capability, memory, evidence, checkpoint, …)
Adapters (vendors, MCP/A2A, Postgres, Redis, object storage)
```

## Anti-patterns

No `BaseAgent` inheritance tree. No SDK types in domain schemas. No business rules only in prompts. No `except Exception: replan`. No unstructured error strings across process boundaries. No tools writing workflow state. No executor self-certifying. No “temporary” port bypass.
