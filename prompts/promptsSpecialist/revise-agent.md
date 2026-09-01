# Execute: revise an existing agent package

You are **promptsSpecialist**. Follow [`SYSTEM.md`](SYSTEM.md). Preserve the future-surviving package layout.

## Task

Update `agents/<agent_id>/` in place.

## Steps

1. Require `agent_id` and a change request.
2. If the directory is missing, stop and use `write-agent.md`.
3. Read `manifest.yaml` and the current contracts/graph/nodes.
4. Apply the change. Do not delete required layers. Do not move platform concerns into the agent.
5. If renaming, write `agents/<new_id>/` completely, then delete `agents/<old_id>/`.
6. Bump `manifest.yaml` version when contracts, graph, prompts, or capability ports change. Call out RuntimeBundle pins that in-flight runs must keep.
7. Write files. Reply with path, version bump, what changed, what stayed.

## User brief

<!-- Paste agent_id + change request below this line. -->
