# promptsSpecialist

Prompts here, when executed, write a **future-surviving agent package** into `/agents`.

| Prompt | Effect |
| --- | --- |
| [`write-agent.md`](write-agent.md) | Create `agents/<agent_id>/` |
| [`revise-agent.md`](revise-agent.md) | Update an existing package |
| [`bootstrap-self.md`](bootstrap-self.md) | Write `agents/prompts_specialist/` |

Load [`SYSTEM.md`](SYSTEM.md), then the execute prompt, plus the brief.

Standard: [`standards/future-surviving-agent.md`](../../standards/future-surviving-agent.md)  
Copy source: [`templates/agent/`](templates/agent)

`agent_id` is snake_case. Do not emit `agents/<name>.md` personas.
