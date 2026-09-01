from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class OpenTelemetryAdapter:
    def __init__(self) -> None:
        self.spans: list[dict[str, Any]] = []
        try:
            from opentelemetry import trace

            self._tracer = trace.get_tracer("highwaysniper")
        except Exception:
            self._tracer = None

    async def emit(self, event: dict[str, Any]) -> None:
        self.spans.append(event)
        if self._tracer:
            with self._tracer.start_as_current_span(event.get("name", "event")):
                pass


class PgVectorAdapter:
    def __init__(self) -> None:
        self._index: dict[str, list[float]] = {}

    async def upsert(self, key: str, vector: list[float], meta: Mapping[str, Any]) -> None:
        self._index[key] = list(vector)

    async def search(self, vector: list[float], k: int = 5) -> list[str]:
        return list(self._index.keys())[:k]
