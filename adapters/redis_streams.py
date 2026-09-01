"""Redis Streams worker groups + in-process fallback (same port)."""

from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from typing import Any


class StreamPort:
    async def xadd(self, stream: str, payload: dict[str, Any]) -> str: ...
    async def xreadgroup(self, group: str, consumer: str, stream: str, count: int = 1) -> list[tuple[str, dict]]: ...
    async def ack(self, stream: str, group: str, msg_id: str) -> None: ...


class InMemoryRedisStreams:
    def __init__(self) -> None:
        self._streams: dict[str, deque[tuple[str, dict[str, Any]]]] = defaultdict(deque)
        self._seq = 0
        self._pending: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)

    async def xadd(self, stream: str, payload: dict[str, Any]) -> str:
        self._seq += 1
        msg_id = str(self._seq)
        self._streams[stream].append((msg_id, payload))
        return msg_id

    async def xreadgroup(self, group: str, consumer: str, stream: str, count: int = 1) -> list[tuple[str, dict]]:
        out: list[tuple[str, dict]] = []
        q = self._streams[stream]
        for _ in range(count):
            if not q:
                break
            msg_id, payload = q.popleft()
            self._pending[group][msg_id] = payload
            out.append((msg_id, payload))
        return out

    async def ack(self, stream: str, group: str, msg_id: str) -> None:
        self._pending[group].pop(msg_id, None)


class RedisStreamsAdapter:
    def __init__(self, url: str | None = None) -> None:
        self.url = url
        self._mem = InMemoryRedisStreams()
        self._redis = None
        if url:
            try:
                import redis.asyncio as redis

                self._redis = redis.from_url(url)
            except Exception:
                self._redis = None

    async def xadd(self, stream: str, payload: dict[str, Any]) -> str:
        if self._redis is None:
            return await self._mem.xadd(stream, payload)
        return await self._redis.xadd(stream, payload)

    async def xreadgroup(self, group: str, consumer: str, stream: str, count: int = 1) -> list[tuple[str, dict]]:
        if self._redis is None:
            return await self._mem.xreadgroup(group, consumer, stream, count)
        return await self._redis.xreadgroup(group, {stream: ">"}, count=count)

    async def ack(self, stream: str, group: str, msg_id: str) -> None:
        if self._redis is None:
            return await self._mem.ack(stream, group, msg_id)
        await self._redis.xack(stream, group, msg_id)


async def wake() -> None:
    await asyncio.sleep(0)
