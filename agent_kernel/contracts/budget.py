from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class BudgetEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True)

    maximum_total_cost: float
    planning: float = 0.0
    execution: float = 0.0
    validation: float = 0.0
    recovery_reserve: float = 0.0
    maximum_duration_seconds: int | None = None
    maximum_model_calls: int | None = None
    maximum_tool_calls: int | None = None
    maximum_child_agents: int = 8
    spent: float = 0.0


class RetryPolicy(BaseModel):
    model_config = ConfigDict(frozen=True)

    maximum_attempts: int = 4
    backoff_seconds: float = 0.2
    jitter: bool = True
    retry_deadline_seconds: float | None = None
    idempotency_key: str | None = None
    retry_budget: int = 8
