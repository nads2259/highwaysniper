from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from agent_kernel.contracts.failure import FailureCategory


class FailureEnvelope(BaseModel):
    """Serializable failure across queues, APIs, and agent boundaries."""

    model_config = ConfigDict(frozen=True)

    code: str
    category: FailureCategory
    message: str
    retryable: bool
    safe_to_repeat: bool
    compensation_required: bool
    retry_after_seconds: int | None = None
    affected_step_ids: list[str] = Field(default_factory=list)
    affected_assumptions: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    cause: FailureEnvelope | None = None
