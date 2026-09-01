from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class EventKind(StrEnum):
    TRANSITION = "transition"
    MODEL_CALL = "model_call"
    TOOL_CALL = "tool_call"
    VALIDATION = "validation"
    MEMORY_WRITE = "memory_write"
    APPROVAL = "approval"
    FAILURE = "failure"


class AgentEvent(BaseModel):
    kind: EventKind
    task_id: str
    at: datetime
    payload: dict[str, object] = Field(default_factory=dict)
