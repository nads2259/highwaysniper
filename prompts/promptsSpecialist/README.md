# promptsSpecialist

Prompts in this directory, when executed, **write an agent file into `/agents`**.

| Prompt | When to execute |
| --- | --- |
| [`write-agent.md`](write-agent.md) | Create a new agent at `agents/<agentName>.md` |
| [`revise-agent.md`](revise-agent.md) | Overwrite an existing agent in `/agents` |
| [`bootstrap-self.md`](bootstrap-self.md) | Write `agents/promptsSpecialist.md` from these prompts |

Load [`SYSTEM.md`](SYSTEM.md) first (system / developer message), then the prompt you want to run (user message), plus your brief.

## Output location

Always:

```text
agents/<agentName>.md
```

`<agentName>` is camelCase, matching this folder’s naming (`promptsSpecialist`).
