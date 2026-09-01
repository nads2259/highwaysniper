from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agent_kernel.contracts.authority import AuthorityGrant
from agent_kernel.contracts.budget import BudgetEnvelope
from agent_kernel.contracts.failure_envelope import FailureEnvelope
from agent_kernel.contracts.plan import Plan
from agent_kernel.contracts.result import AgentResult
from agent_kernel.contracts.runtime_bundle import RuntimeBundle
from agent_kernel.contracts.task import AgentTaskContract
from agent_kernel.lifecycle import Lifecycle


class CompiledContext(BaseModel):
    trusted_instructions: list[str] = Field(default_factory=list)
    untrusted_data: list[str] = Field(default_factory=list)
    provenance: dict[str, str] = Field(default_factory=dict)
    token_estimate: int = 0
    injection_flags: list[str] = Field(default_factory=list)
    why_included: list[str] = Field(default_factory=list)


class AgentState(BaseModel):
    """Per-instance working memory. Never stored on the agent type."""

    lifecycle: Lifecycle = Lifecycle.RECEIVED
    task: AgentTaskContract | None = None
    plan: Plan | None = None
    compiled_plan: list[str] = Field(default_factory=list)
    context: CompiledContext = Field(default_factory=CompiledContext)
    step_results: dict[str, Any] = Field(default_factory=dict)
    validated_steps: set[str] = Field(default_factory=set)
    result: AgentResult | None = None
    replan_count: int = 0
    max_replans: int = 5
    reflection_count: int = 0
    max_reflections: int = 8
    delegation_depth: int = 0
    max_delegation_depth: int = 4
    budget: BudgetEnvelope | None = None
    authority: AuthorityGrant | None = None
    runtime_bundle: RuntimeBundle | None = None
    failure: FailureEnvelope | None = None
    cancelled: bool = False
    paused_for_approval: bool = False
    events: list[dict[str, Any]] = Field(default_factory=list)
