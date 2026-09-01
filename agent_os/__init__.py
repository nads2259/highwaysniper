"""Agent OS: platform concerns agents must not privately reimplement."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from agent_kernel.contracts.lease import TaskLease
from agent_kernel.contracts.memory import CheckpointRecord, EvidenceRecord, MemoryRecord
from agent_kernel.errors import AuthorizationDeniedError, SecurityError
from agent_kernel.lifecycle import Lifecycle
from agent_kernel.scheduler import InMemoryLeasePort


class TenantIsolation:
    def __init__(self) -> None:
        self._tenants: dict[str, set[str]] = {}

    def bind(self, tenant: str, resource: str) -> None:
        self._tenants.setdefault(tenant, set()).add(resource)

    def assert_owns(self, tenant: str, resource: str) -> None:
        if resource not in self._tenants.get(tenant, set()):
            raise AuthorizationDeniedError(f"{tenant} cannot access {resource}")


class IdentityRegistry:
    """AGNTCY-compatible identity records (canonical, not vendor-locked)."""

    def __init__(self) -> None:
        self._ids: dict[str, dict[str, Any]] = {}

    def register(self, agent_id: str, capabilities: list[str], public_key: str = "local") -> dict[str, Any]:
        doc = {
            "id": agent_id,
            "capabilities": capabilities,
            "public_key": public_key,
            "digest": hashlib.sha256(agent_id.encode()).hexdigest(),
        }
        self._ids[agent_id] = doc
        return doc

    def verify(self, agent_id: str) -> dict[str, Any]:
        if agent_id not in self._ids:
            raise SecurityError(f"unknown agent {agent_id}")
        return self._ids[agent_id]


class SecretVault:
    def __init__(self) -> None:
        self._secrets: dict[str, str] = {}

    def put(self, name: str, value: str) -> None:
        self._secrets[name] = value

    def issue_scoped(self, name: str, grant_id: str) -> str:
        if name not in self._secrets:
            raise SecurityError(f"missing secret {name}")
        return f"scoped:{grant_id}:{name}"


class QuotaBoard:
    def __init__(self, global_concurrency: int = 1024) -> None:
        self.global_concurrency = global_concurrency
        self.active = 0

    def enter(self) -> None:
        if self.active >= self.global_concurrency:
            raise RuntimeError("global concurrency limit")
        self.active += 1

    def leave(self) -> None:
        self.active = max(0, self.active - 1)


class Sandbox:
    def __init__(self, profile: str = "restricted") -> None:
        self.profile = profile
        self.allowed = {"echo", "hash", "domain"}

    async def run(self, capability: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if capability not in self.allowed:
            raise SecurityError(f"sandbox denied {capability}")
        if capability == "hash":
            return {"digest": hashlib.sha256(json.dumps(arguments, sort_keys=True).encode()).hexdigest()}
        return {"ok": True, "capability": capability, "arguments": arguments}


class ApprovalRouter:
    def __init__(self) -> None:
        self.pending: dict[str, dict[str, Any]] = {}
        self.decisions: dict[str, bool] = {}

    async def request(self, reason: str, payload: dict[str, Any]) -> str:
        rid = str(uuid4())
        self.pending[rid] = {"reason": reason, "payload": payload}
        return rid

    def decide(self, rid: str, approved: bool) -> None:
        self.decisions[rid] = approved

    def resume_allowed(self, rid: str) -> bool:
        return self.decisions.get(rid, False)


class AppendOnlyLedger:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path
        self._rows: list[dict[str, Any]] = []

    async def append(self, event: dict[str, Any]) -> None:
        row = {**event, "seq": len(self._rows), "at": datetime.now(timezone.utc).isoformat()}
        self._rows.append(row)
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(row) + "\n")

    def replay(self) -> list[dict[str, Any]]:
        return list(self._rows)


class SqliteCheckpoint:
    """Durable checkpointer (file-backed). Postgres adapter uses the same SQL."""

    def __init__(self, path: Path) -> None:
        import sqlite3

        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(path)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS checkpoints (task_id TEXT, lifecycle TEXT, at TEXT, digest TEXT)"
        )
        self._conn.commit()

    async def save(self, record: CheckpointRecord) -> None:
        self._conn.execute(
            "INSERT INTO checkpoints VALUES (?,?,?,?)",
            (record.task_id, record.lifecycle.value, record.at.isoformat(), record.payload_digest),
        )
        self._conn.commit()

    def load(self, task_id: str) -> list[tuple]:
        cur = self._conn.execute("SELECT * FROM checkpoints WHERE task_id=?", (task_id,))
        return cur.fetchall()


class FileArtifactStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        root.mkdir(parents=True, exist_ok=True)

    async def put(self, name: str, data: bytes) -> str:
        dest = self.root / name
        dest.write_bytes(data)
        return str(dest)


class KillSwitch:
    def __init__(self) -> None:
        self.killed = False

    def kill(self) -> None:
        self.killed = True

    def assert_alive(self) -> None:
        if self.killed:
            raise RuntimeError("kill switch engaged")


class Health:
    def __init__(self) -> None:
        self.ready = True
        self.live = True

    def endpoints(self) -> dict[str, bool]:
        return {"health": self.live, "ready": self.ready}


@dataclass
class AgentOS:
    identity: IdentityRegistry = field(default_factory=IdentityRegistry)
    tenants: TenantIsolation = field(default_factory=TenantIsolation)
    secrets: SecretVault = field(default_factory=SecretVault)
    quotas: QuotaBoard = field(default_factory=QuotaBoard)
    sandbox: Sandbox = field(default_factory=Sandbox)
    approvals: ApprovalRouter = field(default_factory=ApprovalRouter)
    ledger: AppendOnlyLedger = field(default_factory=AppendOnlyLedger)
    leases: InMemoryLeasePort = field(default_factory=InMemoryLeasePort)
    artifacts: FileArtifactStore | None = None
    checkpoints: SqliteCheckpoint | None = None
    kill_switch: KillSwitch = field(default_factory=KillSwitch)
    health: Health = field(default_factory=Health)

    @classmethod
    def local(cls, root: Path) -> AgentOS:
        os = cls(
            ledger=AppendOnlyLedger(root / "ledger.jsonl"),
            artifacts=FileArtifactStore(root / "artifacts"),
            checkpoints=SqliteCheckpoint(root / "checkpoints.sqlite"),
        )
        return os
