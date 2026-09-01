"""Repair/replan: classified failures only. Reuse validated branches still in-assumption."""

from agent_kernel.lifecycle import Lifecycle

from ..graph.lifecycle import checkpoint_after
from ..graph.state import AgentState


def replanner(state: AgentState) -> dict:
    if state.replan_count >= state.max_replans:
        return {"lifecycle": checkpoint_after(state.lifecycle, Lifecycle.GOAL_VALIDATION)}
    nxt = (
        checkpoint_after(Lifecycle.REPLANNING, Lifecycle.PLAN_VALIDATION)
        if state.lifecycle == Lifecycle.REPLANNING
        else state.lifecycle
    )
    return {"replan_count": state.replan_count + 1, "lifecycle": nxt}
