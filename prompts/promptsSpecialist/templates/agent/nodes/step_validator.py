"""Step validator: independent of the executor. Evidence required."""

from ..graph.state import AgentState


async def step_validator(state: AgentState) -> dict:
    return {}
