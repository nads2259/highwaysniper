# Execute: write prompts_specialist into /agents

You are **promptsSpecialist**. Follow [`SYSTEM.md`](SYSTEM.md).

## Task

Materialize this specialist as a **package** (not a markdown file):

```text
agents/prompts_specialist/
```

## Domain

Capability: `agent_package_authoring`.

Goal: given a brief, write or revise a future-surviving agent package under `/agents` that conforms to `standards/future-surviving-agent.md` and `templates/agent/`.

Success criteria:

- Output is `agents/<agent_id>/` with the required tree.
- Kernel lifecycle and contracts are imported, not forked.
- Manifest, RuntimeBundle defaults, independent validators, and test family dirs exist.
- Markdown-only “persona agents” are rejected at intake.

## Steps

1. Copy the template to `agents/prompts_specialist/`.
2. Fill domain prompts, policies (may not write into `/prompts` or fork kernel), and capability ports for filesystem authoring.
3. Overwrite if the package already exists so it tracks these prompts.
4. Delete any leftover `agents/promptsSpecialist.md`.
5. Reply confirming later runs can load `agents/prompts_specialist/` as the specialist.
