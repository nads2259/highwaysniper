from __future__ import annotations

from datetime import datetime, timezone

from agent_kernel.contracts.memory import MemoryKind, MemoryRecord
from agent_kernel.errors import SecurityError, ValidationFailedError


class GovernedMemory:
    """Six stores. Hypotheses never become semantic truth without validation."""

    def __init__(self) -> None:
        self._stores: dict[MemoryKind, dict[str, MemoryRecord]] = {k: {} for k in MemoryKind}

    async def write(self, record: MemoryRecord) -> None:
        if record.kind == MemoryKind.SEMANTIC and not record.validated:
            raise ValidationFailedError("semantic writes require validation")
        if not record.provenance:
            raise SecurityError("memory write missing provenance")
        self._stores[record.kind][record.key] = record

    async def read(self, kind: MemoryKind, key: str) -> MemoryRecord | None:
        rec = self._stores[kind].get(key)
        if rec and rec.expires_at and rec.expires_at < datetime.now(timezone.utc):
            return None
        return rec

    def working_clear(self) -> None:
        self._stores[MemoryKind.WORKING].clear()
