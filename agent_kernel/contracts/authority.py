from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuthorityGrant(BaseModel):
    """Short-lived, scope-bound delegated authority. Never the user's full credentials."""

    model_config = ConfigDict(frozen=True)

    initiator: str
    mission_id: str
    agent_id: str
    task_id: str
    on_behalf_of: str
    permissions: list[str] = Field(default_factory=list)
    resource: str | None = None
    expires_at: datetime | None = None
    delegatable: bool = False
    revocable: bool = True
