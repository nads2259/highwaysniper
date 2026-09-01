"""Narrow async ports. Domain depends on these; SDKs stay in adapters."""

from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

from agent_kernel.contracts.lease import TaskLease
from agent_kernel.contracts.memory import CheckpointRecord, EvidenceRecord, MemoryRecord
from agent_kernel.contracts.model import ModelRequest, ModelResponse, ToolRequest, ToolResult


class ChatModelPort(Protocol):
    async def generate(self, request: ModelRequest) -> ModelResponse: ...


class EmbeddingModelPort(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class ToolExecutionPort(Protocol):
    async def execute(self, request: ToolRequest) -> ToolResult: ...


class MemoryPort(Protocol):
    async def write(self, record: MemoryRecord) -> None: ...

    async def read(self, key: str) -> MemoryRecord | None: ...


class CheckpointPort(Protocol):
    async def save(self, record: CheckpointRecord) -> None: ...


class ArtifactPort(Protocol):
    async def put(self, name: str, data: bytes) -> str: ...


class ApprovalPort(Protocol):
    async def request(self, reason: str, payload: dict[str, Any]) -> str: ...


class PolicyPort(Protocol):
    async def allow(self, action: str, resource: str) -> bool: ...


class TelemetryPort(Protocol):
    async def emit(self, event: dict[str, Any]) -> None: ...


class EvidencePort(Protocol):
    async def record(self, record: EvidenceRecord) -> None: ...


class LeasePort(Protocol):
    async def acquire(self, task_id: str, worker_id: UUID) -> TaskLease: ...

    async def heartbeat(self, lease: TaskLease) -> TaskLease: ...


class CapabilityPort(Protocol):
    async def invoke(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]: ...


class ValidationPort(Protocol):
    async def validate(self, subject: Any, contract: Any) -> dict[str, Any]: ...
