# Agents

Packages written by [`prompts/promptsSpecialist`](../prompts/promptsSpecialist):

```text
agents/<agent_id>/
```

Each package is a durable goal processor. Instantiate per run: `await AgentType().spawn().execute(task)`. 100 concurrent executions = 100 instances. Standard: [`standards/future-surviving-agent.md`](../standards/future-surviving-agent.md), engineering: [`standards/engineering.md`](../standards/engineering.md).

Do not add markdown persona files here.
