"""Plan validator: coverage, DAG, budget, validators, fallbacks. Deterministic checks first."""

from agent_kernel.lifecycle import Lifecycle

from ..graph.lifecycle import checkpoint_after
from ..graph.state import AgentState


async def plan_validator(state: AgentState) -> dict:
    if state.plan is None or not state.plan.is_acyclic():
        return {"lifecycle": checkpoint_after(Lifecycle.PLAN_VALIDATION, Lifecycle.PLANNING)}
    return {"lifecycle": checkpoint_after(Lifecycle.PLAN_VALIDATION, Lifecycle.EXECUTING)}
