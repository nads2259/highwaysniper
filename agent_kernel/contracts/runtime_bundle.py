from __future__ import annotations

from pydantic import BaseModel, Field


class ModelRequirement(BaseModel):
    roles: list[str]
    required: list[str] = Field(default_factory=list)
    preferred: list[str] = Field(default_factory=list)
    constraints: dict[str, object] = Field(default_factory=dict)


class RuntimeBundle(BaseModel):
    """Frozen operating environment for one run. New versions do not mutate in-flight work."""

    agent_version: str
    graph_version: int
    task_contract_version: int
    result_contract_version: int
    models: dict[str, str] = Field(default_factory=dict)
    prompts: dict[str, str] = Field(default_factory=dict)
    capabilities: dict[str, str] = Field(default_factory=dict)
    policies: dict[str, str] = Field(default_factory=dict)
    dependencies: dict[str, str] = Field(default_factory=dict)
    memory_profile: str | None = None
    checkpoint_profile: str | None = None
    sandbox_profile: str | None = None
    tool_registry_version: int | None = None
    container_digest: str | None = None
    package_lock_hash: str | None = None
