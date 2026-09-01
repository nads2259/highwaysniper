# highwaysniper

Contract-driven agents: deterministic kernel, domain packages, specialist prompts that write those packages.

```text
standards/          # architecture, engineering, spec coverage
agent_kernel/       # contracts, lifecycle, ports, Agent/AgentRun
prompts/<name>/     # executable specialist prompts
agents/<agent_id>/  # independently deployable agent packages
```

Run one execution as an **instance**: `await PromptsSpecialist().spawn().execute(task)`. One hundred concurrent runs are one hundred `spawn()`s.

Create an agent by loading `prompts/promptsSpecialist/SYSTEM.md` then `write-agent.md`. Output is `agents/<agent_id>/`.

