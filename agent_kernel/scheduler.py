"""DAG scheduler: concurrent ready tasks, leases, isolated envelopes, reducer."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from agent_kernel.contracts.lease import TaskLease
from agent_kernel.contracts.plan import Plan, PlanStep
from agent_kernel.errors import LeaseLostError


Envelope = dict[str, object]
StepFn = Callable[[PlanStep, TaskLease], Awaitable[Envelope]]


class InMemoryLeasePort:
    def __init__(self) -> None:
        self._leases: dict[str, TaskLease] = {}
        self._tokens: dict[str, int] = {}

    async def acquire(self, task_id: str, worker_id: UUID) -> TaskLease:
        now = datetime.now(timezone.utc)
        token = self._tokens.get(task_id, 0) + 1
        self._tokens[task_id] = token
        lease = TaskLease(
            task_id=task_id,
            worker_id=worker_id,
            fencing_token=token,
            acquired_at=now,
            expires_at=now + timedelta(seconds=30),
        )
        self._leases[task_id] = lease
        return lease

    async def heartbeat(self, lease: TaskLease) -> TaskLease:
        current = self._leases.get(lease.task_id)
        if current is None or current.fencing_token != lease.fencing_token:
            raise LeaseLostError(lease.task_id)
        return await self.acquire(lease.task_id, lease.worker_id)


async def run_dag(
    plan: Plan,
    execute_step: StepFn,
    *,
    max_parallel: int = 4,
    lease_port: InMemoryLeasePort | None = None,
    cancel: asyncio.Event | None = None,
) -> dict[str, Envelope]:
    leases = lease_port or InMemoryLeasePort()
    completed: set[str] = set()
    envelopes: dict[str, Envelope] = {}
    sem = asyncio.Semaphore(max_parallel)
    failed: dict[str, str] = {}

    async def _one(step: PlanStep) -> None:
        if cancel and cancel.is_set():
            return
        async with sem:
            worker = uuid4()
            lease = await leases.acquire(step.id, worker)
            try:
                envelopes[step.id] = await execute_step(step, lease)
                completed.add(step.id)
            except Exception as exc:  # noqa: BLE001 — envelope isolation, not swallow-to-replan
                failed[step.id] = str(exc)
                envelopes[step.id] = {"ok": False, "error": str(exc)}

    while True:
        if cancel and cancel.is_set():
            break
        ready = [s for s in plan.ready_steps(completed) if s.id not in failed and s.id not in envelopes]
        if not ready:
            if len(completed) + len(failed) >= len(plan.steps) or not plan.ready_steps(completed | set(failed)):
                break
            if not plan.ready_steps(completed) and failed:
                break
            break
        await asyncio.gather(*[_one(step) for step in ready])
    return envelopes
