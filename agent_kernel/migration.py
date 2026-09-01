from __future__ import annotations

from collections.abc import Callable
from typing import Any


class SchemaMigrator:
    def __init__(self, name: str, version: int) -> None:
        self.name = name
        self.version = version
        self._up: dict[int, Callable[[dict[str, Any]], dict[str, Any]]] = {}
        self._down: dict[int, Callable[[dict[str, Any]], dict[str, Any]]] = {}
        self.unknown_field_policy = "preserve"
        self.deprecation: str | None = None

    def register(self, from_version: int, up: Callable, down: Callable) -> None:
        self._up[from_version] = up
        self._down[from_version + 1] = down

    def upcast(self, payload: dict[str, Any], from_version: int) -> dict[str, Any]:
        data = dict(payload)
        v = from_version
        while v < self.version:
            if v not in self._up:
                raise ValueError(f"no upcast {self.name} {v}->{v+1}")
            data = self._up[v](data)
            v += 1
        return data

    def downcast(self, payload: dict[str, Any], to_version: int) -> dict[str, Any]:
        data = dict(payload)
        v = self.version
        while v > to_version:
            if v not in self._down:
                raise ValueError(f"no downcast {self.name} {v}->{v-1}")
            data = self._down[v](data)
            v -= 1
        return data
