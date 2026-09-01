from __future__ import annotations

from pydantic import BaseModel, Field


class GoalContract(BaseModel):
    statement: str
    success_criteria: list[str]


class ScopeContract(BaseModel):
    allowed_resources: list[str] = Field(default_factory=list)
    excluded_resources: list[str] = Field(default_factory=list)


class ConstraintContract(BaseModel):
    deadline: str | None = None
    max_cost_usd: float | None = None
    max_steps: int | None = None
    max_parallel_tasks: int = 4
    permitted_tools: list[str] = Field(default_factory=list)
    prohibited_actions: list[str] = Field(default_factory=list)


class ValidationContract(BaseModel):
    required_validators: list[str] = Field(
        default_factory=lambda: ["schema", "evidence", "domain", "policy"]
    )
    minimum_confidence: float = 0.9


class ExecutionContract(BaseModel):
    idempotency_key: str
    retry_policy: str = "classified"
    checkpoint_policy: str = "after_transition"


class AgentRef(BaseModel):
    capability: str
    required_version: str = ">=0.1,<1.0"


class AgentTaskContract(BaseModel):
    """Immutable invocation contract. Not a raw prompt."""

    task_id: str
    mission_id: str
    agent: AgentRef
    goal: GoalContract
    scope: ScopeContract = Field(default_factory=ScopeContract)
    inputs: dict[str, object] = Field(default_factory=dict)
    constraints: ConstraintContract = Field(default_factory=ConstraintContract)
    validation: ValidationContract = Field(default_factory=ValidationContract)
    execution: ExecutionContract
    output_schema: str
    runtime_bundle: dict[str, object] | None = None
