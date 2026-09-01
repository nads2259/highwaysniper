# Execute: write promptsSpecialist into /agents

You are running as **promptsSpecialist**. Follow [`SYSTEM.md`](SYSTEM.md) and [`templates/agent.md`](templates/agent.md).

## Your task

Materialize **this specialist** as an agent file in the agents root so later sessions can load one file instead of this prompt folder.

**Write:**

```text
agents/promptsSpecialist.md
```

## What the agent must encode

The file must stand alone. Collapse `SYSTEM.md`, `write-agent.md`, `revise-agent.md`, and the template contract into one agent definition.

It must instruct the loaded agent to:

- Create new agents at `agents/<agentName>.md` (same rules as `write-agent.md`).
- Revise existing agents in `/agents` (same rules as `revise-agent.md`).
- Never write agent files into `/prompts`.
- Use camelCase names matching `promptsSpecialist`.
- Use the template sections: Identity, Scope, Inputs, Process, Outputs, Done when, Refusals, plus YAML `name`, `title`, `role`, `description`.

## Steps

1. Read every file in `prompts/promptsSpecialist/` including the template.
2. Draft `agents/promptsSpecialist.md` so an LLM that sees only that file behaves as this specialist.
3. If `agents/promptsSpecialist.md` already exists, overwrite it so it matches these prompts.
4. **Write** the file. Do not only print it in chat.
5. Reply with the path and confirm a later session can run from `agents/promptsSpecialist.md` alone.
