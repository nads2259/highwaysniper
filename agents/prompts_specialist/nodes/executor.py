"""Executor: tools/models/subagents only through sandboxed capability gateways."""

from ..graph.state import AgentState


async def executor(state: AgentState) -> dict:
    return {}
