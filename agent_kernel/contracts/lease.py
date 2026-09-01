from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TaskLease(BaseModel):
    model_config = ConfigDict(frozen=True)

    task_id: str
    worker_id: UUID
    fencing_token: int
    acquired_at: datetime
    expires_at: datetime
