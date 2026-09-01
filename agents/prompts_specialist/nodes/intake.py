"""Intake: schema, support, and safety. Reject before planning."""

from agent_kernel.lifecycle import Lifecycle

from ..graph.lifecycle import checkpoint_after
from ..graph.state import AgentState


async def intake(state: AgentState) -> dict:
    if state.task is None:
        raise ValueError("AgentTaskContract required")
    return {"lifecycle": checkpoint_after(state.lifecycle, Lifecycle.CONTRACTED)}
