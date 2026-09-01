"""Goal manager: measurable goal, constraints, acceptance. Not a restated prompt."""

from agent_kernel.lifecycle import Lifecycle

from ..graph.lifecycle import checkpoint_after
from ..graph.state import AgentState


async def goal_builder(state: AgentState) -> dict:
    assert state.task is not None
    if not state.task.goal.success_criteria:
        raise ValueError("goal.success_criteria is required")
    return {"lifecycle": checkpoint_after(state.lifecycle, Lifecycle.PLANNING)}
