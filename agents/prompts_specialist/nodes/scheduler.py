"""Scheduler: lease ready DAG tasks. Bounded fan-out. Isolated result envelopes."""

from ..graph.state import AgentState


def scheduler(state: AgentState) -> dict:
    return {}
