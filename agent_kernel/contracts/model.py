from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ModelRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    role: str
    messages: list[dict[str, str]]
    require_structured_output: bool = False
    tools: list[str] = Field(default_factory=list)


class ModelResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    content: str
    refusal: bool = False
    usage_tokens: int = 0
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)


class ToolRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str
    authority_grant_id: str | None = None


class ToolResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    ok: bool
    payload: dict[str, Any] = Field(default_factory=dict)
    receipt_id: str
