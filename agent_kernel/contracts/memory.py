from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from agent_kernel.lifecycle import Lifecycle


class MemoryKind(StrEnum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    ARTIFACT = "artifact"
    EVIDENCE_LEDGER = "evidence_ledger"


class MemoryRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    kind: MemoryKind
    key: str
    payload: dict[str, object] = Field(default_factory=dict)
    provenance: str
    validated: bool = False
    tenant: str | None = None
    expires_at: datetime | None = None


class EvidenceRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    claim_ref: str
    source: str
    artifact_uri: str | None = None
    validator: str
    at: datetime


class CheckpointRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    task_id: str
    lifecycle: Lifecycle
    at: datetime
    payload_digest: str


class CapabilitySupplyChain(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    version: str
    digest: str
    publisher: str
    side_effect_class: str
    idempotent: bool
    sandbox_profile: str
    revoked: bool = False
