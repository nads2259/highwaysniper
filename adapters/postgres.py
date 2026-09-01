"""Postgres-shaped checkpoint SQL. File sqlite is the default durable engine; DSN selects driver."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from agent_kernel.contracts.memory import CheckpointRecord
from agent_os import SqliteCheckpoint

DDL = """
CREATE TABLE IF NOT EXISTS checkpoints (
  task_id TEXT NOT NULL,
  lifecycle TEXT NOT NULL,
  at TEXT NOT NULL,
  digest TEXT NOT NULL
)
"""


class PostgresCheckpointAdapter:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        if dsn.startswith("sqlite:"):
            self._impl = SqliteCheckpoint(Path(dsn.split("sqlite:", 1)[1]))
        elif dsn.startswith("postgres"):
            self._impl = None
            self._connect_postgres()
        else:
            self._impl = SqliteCheckpoint(Path(dsn))

    def _connect_postgres(self) -> None:
        try:
            import psycopg

            self._pg = psycopg.connect(self.dsn)
            self._pg.execute(DDL)
            self._pg.commit()
        except Exception as exc:  # driver optional; contract still present
            raise RuntimeError(f"postgres unavailable: {exc}") from exc

    async def save(self, record: CheckpointRecord) -> None:
        if self._impl:
            await self._impl.save(record)
            return
        self._pg.execute(
            "INSERT INTO checkpoints VALUES (%s,%s,%s,%s)",
            (record.task_id, record.lifecycle.value, record.at.isoformat(), record.payload_digest),
        )
        self._pg.commit()
