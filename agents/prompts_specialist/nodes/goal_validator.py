"""Goal evaluator: acceptance criteria, not plan completion."""

from ..graph.state import AgentState


async def goal_validator(state: AgentState) -> dict:
    return {}
