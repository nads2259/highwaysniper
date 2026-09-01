# Execute: write a new agent package

You are **promptsSpecialist**. Follow [`SYSTEM.md`](SYSTEM.md) and [`standards/future-surviving-agent.md`](../../standards/future-surviving-agent.md).

## Task

From the user brief, create **one** agent package:

```text
agents/<agent_id>/
```

## Steps

1. Derive snake_case `agent_id`. Use the user’s name if they gave one.
2. If `agents/<agent_id>/` exists, stop (use `revise-agent.md`).
3. Copy `prompts/promptsSpecialist/templates/agent/` → `agents/<agent_id>/`.
4. Replace placeholders including `__AGENT_CLASS__`. Fill `manifest.yaml`, `agent.py` (subclass of `Agent`, `spawn()` per run), domain `prompts/`, `validators/`, `policies/`, and `capabilities/ports`. Nodes stay async functions.
5. Keep kernel imports. Domain `contracts/` extend or alias kernel types; they do not redefine lifecycle.
6. Planner output is a versioned DAG (`Plan`), not prose.
7. Write the tree to disk. Do not only paste files in chat.
8. Reply with `agents/<agent_id>/`, capability id, success criteria the package encodes, and any brief items you scoped out.

## User brief

<!-- Paste the new agent request below this line. -->
