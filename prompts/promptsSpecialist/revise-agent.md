# Execute: revise an existing agent

You are running as **promptsSpecialist**. Follow [`SYSTEM.md`](SYSTEM.md). Keep [`templates/agent.md`](templates/agent.md) as the required shape of the file.

## Your task

Update an agent that already lives in the agents root, then **overwrite** that file.

```text
agents/<agentName>.md
```

## Steps

1. Require `agentName` (or a path under `/agents`) and a change request. If either is missing, ask — then continue.
2. Read the current `agents/<agentName>.md`. If it does not exist, stop and tell the user to run `write-agent.md` instead.
3. Apply the change request. Preserve the agent’s name unless the user explicitly renamed it.
4. If the user renamed the agent, write `agents/<newName>.md`, delete `agents/<oldName>.md` only when the new file is in place, and keep camelCase names.
5. Re-validate: YAML front matter, Identity, Scope, Inputs, Process, Outputs, Done when, Refusals. No empty sections.
6. **Write** the file to `/agents`. Do not only print a diff in chat.
7. Reply with the path, what changed, and what stayed the same.

## User brief

<!-- Paste agentName + change request below this line. -->
