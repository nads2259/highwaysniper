from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agent_kernel.contracts.plan import Plan
from agent_kernel.contracts.result import AgentResult
from agent_kernel.contracts.task import AgentTaskContract
from agent_kernel.lifecycle import Lifecycle


class AgentState(BaseModel):
    """Per-instance working memory. Never stored on the agent type."""

    lifecycle: Lifecycle = Lifecycle.RECEIVED
    task: AgentTaskContract | None = None
    plan: Plan | None = None
    step_results: dict[str, Any] = Field(default_factory=dict)
    result: AgentResult | None = None
    replan_count: int = 0
    max_replans: int = 5
