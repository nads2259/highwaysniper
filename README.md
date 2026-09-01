# highwaysniper

Contract-driven, independently deployable agents. An agent is not an LLM with tools and a ReAct loop. It is a **durable goal processor**:

> Understand → contract → plan → validate plan → schedule → execute safely → validate evidence → repair/replan → complete or escalate.

**Deterministic control shell; agentic intelligence only at named decision points.** Planning may be probabilistic. State transitions, permissions, retries, budgets, evidence, and acceptance are deterministic.

SOLID and OOP structure that shell. Graph nodes are async functions, not a class hierarchy of prompts. Provider SDKs stay behind ports.

## Layout

```text
standards/                 Architecture, engineering rules, coverage map
agent_kernel/              Contracts, lifecycle, scheduler, validators, Agent / AgentRun
agent_os/                  Identity, tenants, secrets, quotas, sandbox, ledger, checkpoints
adapters/                  REST, gRPC, queue, MCP, A2A, AGNTCY, LangGraph, Postgres, Redis, OTel
evaluations/               Evaluation families and release gates
release/                   Signed runtime-bundle pipeline
evolution/                 Improvement proposals (cannot mutate production)
prompts/<specialistName>/  Executable specialist prompts
agents/<agent_id>/         Independently deployable agent packages
```

Canonical types live in `agent_kernel`. MCP, A2A, AGNTCY, and LangGraph are adapters. Domain agents import the kernel; they do not fork a second lifecycle.

Full spec: [`standards/future-surviving-agent.md`](standards/future-surviving-agent.md)  
Engineering: [`standards/engineering.md`](standards/engineering.md)  
Coverage map: [`standards/coverage.md`](standards/coverage.md)

## Run an agent

An **agent type** holds ports and node implementations. A **run** is a new instance with isolated working state. One hundred concurrent executions means one hundred instances.

```python
import asyncio
from agents.prompts_specialist.agent import PromptsSpecialist
from agent_kernel.contracts.task import (
    AgentRef,
    AgentTaskContract,
    ExecutionContract,
    GoalContract,
)

agent = PromptsSpecialist()  # type; no per-run state

task = AgentTaskContract(
    task_id="task-1",
    mission_id="mission-1",
    agent=AgentRef(capability="agent_package_authoring"),
    goal=GoalContract(
        statement="Author an agent package",
        success_criteria=["tree exists", "kernel imported"],
    ),
    execution=ExecutionContract(idempotency_key="task-1"),
    output_schema="AgentPackageAuthoringResultV1",
)

result = asyncio.run(agent.spawn().execute(task))

# concurrent
results = asyncio.run(
    asyncio.gather(*[agent.spawn().execute(task) for _ in range(8)])
)
```

Success is **goal acceptance**, not a successful tool call. Terminal statuses include partial success, blocked, approval required, budget exhausted, and policy denied — never coerced into `Succeeded`.

## Create an agent

Specialist prompts write packages into `/agents`. They do not write markdown personas.

1. Load [`prompts/promptsSpecialist/SYSTEM.md`](prompts/promptsSpecialist/SYSTEM.md).
2. Run [`write-agent.md`](prompts/promptsSpecialist/write-agent.md) with a brief (capability, success criteria, permitted tools).
3. Output is `agents/<agent_id>/` (`snake_case`), copied from [`prompts/promptsSpecialist/templates/agent/`](prompts/promptsSpecialist/templates/agent) and filled in.

Each package exposes `agent.py` with a subclass of `agent_kernel.runtime.Agent`. Required tree: `manifest.yaml`, contracts, graph, nodes, capability ports/adapters, validators, policies, prompts, memory, evidence, telemetry, evolution, and the test families under `tests/`.

Revise with [`revise-agent.md`](prompts/promptsSpecialist/revise-agent.md). Refresh the specialist package with [`bootstrap-self.md`](prompts/promptsSpecialist/bootstrap-self.md).

## Install and test

Python 3.11+.

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest -q
```

Postgres, Redis, and OpenTelemetry adapters use the same ports as the in-process backends. Point a DSN/URL at a live service when you have one; local tests do not require those processes.

## License

See the repository for license terms if present; otherwise all rights reserved by the owner.
