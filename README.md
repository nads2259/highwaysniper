# highwaysniper

## Layout

```text
prompts/<specialistName>/   # executable prompts
agents/                     # agents written by those prompts
```

Start with [`prompts/promptsSpecialist`](prompts/promptsSpecialist): load `SYSTEM.md`, then run `write-agent.md` (or `bootstrap-self.md`) so a new file appears in [`agents/`](agents).
