"""Finalizer: emit AgentResult. Never convert partial or uncertain work into Succeeded."""

from ..graph.state import AgentState


async def finalizer(state: AgentState) -> dict:
    return {}
