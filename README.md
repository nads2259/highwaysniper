# highwaysniper

Contract-driven agents: deterministic kernel, domain packages, specialist prompts that write those packages.

```text
standards/          # future-surviving agent standard
agent_kernel/       # canonical contracts, lifecycle, protocol names
prompts/<name>/     # executable specialist prompts
agents/<agent_id>/  # independently deployable agent packages
```

Create an agent by loading `prompts/promptsSpecialist/SYSTEM.md` then `write-agent.md` with a brief. Output is `agents/<agent_id>/`, not a single markdown file.
