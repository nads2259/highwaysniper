from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Awaitable, Callable
from uuid import uuid4

from agent_kernel.contracts.memory import CheckpointRecord
from agent_kernel.contracts.result import AgentResult
from agent_kernel.contracts.task import AgentTaskContract
from agent_kernel.errors import NonConvergingPlanError
from agent_kernel.lifecycle import Lifecycle, TerminalStatus, assert_transition
from agent_kernel.nodes_default import KernelNodes
from agent_kernel.state import AgentState
from agent_os import AgentOS

NodeFn = Callable[[AgentState], Awaitable[dict[str, Any]]]


@dataclass
class Agent:
    """Reusable agent type. No per-run mutable state.

    100 concurrent executions: 100 ``spawn()`` instances (or 100 ``Agent()`` constructions).
    """

    name: str
    os: AgentOS = field(default_factory=AgentOS)
    nodes: Any = None
    ports: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.nodes is None:
            self.nodes = KernelNodes(self.os)

    def spawn(self) -> AgentRun:
        return AgentRun(name=self.name, nodes=self.nodes, ports=self.ports, os=self.os)

    async def execute(self, task: AgentTaskContract) -> AgentResult:
        return await self.spawn().execute(task)


@dataclass
class AgentRun:
    """One isolated async execution. Do not reuse across tasks."""

    name: str
    nodes: Any
    ports: dict[str, Any]
    os: AgentOS
    run_id: str = field(default_factory=lambda: str(uuid4()))
    state: AgentState = field(default_factory=AgentState)

    def _apply(self, current: Lifecycle, updates: dict[str, Any]) -> None:
        nxt = updates.get("lifecycle")
        if nxt is not None and nxt != current:
            assert_transition(current, nxt)
        self.state = self.state.model_copy(update=updates)

    async def _checkpoint(self) -> None:
        if not self.state.task:
            return
        digest = sha256(self.state.model_dump_json().encode()).hexdigest()
        record = CheckpointRecord(
            task_id=self.state.task.task_id,
            lifecycle=self.state.lifecycle,
            at=datetime.now(timezone.utc),
            payload_digest=digest,
        )
        if self.os.checkpoints:
            await self.os.checkpoints.save(record)
        await self.os.ledger.append(
            {"kind": "transition", "run_id": self.run_id, "lifecycle": self.state.lifecycle.value}
        )

    async def execute(self, task: AgentTaskContract) -> AgentResult:
        self.os.quotas.enter()
        try:
            return await self._execute(task)
        finally:
            self.os.quotas.leave()

    async def _execute(self, task: AgentTaskContract) -> AgentResult:
        self.state = AgentState(task=task, lifecycle=Lifecycle.RECEIVED)
        handlers: dict[Lifecycle, NodeFn] = {
            Lifecycle.RECEIVED: self.nodes.intake,
            Lifecycle.CONTRACTED: self.nodes.goal_builder,
            Lifecycle.PLANNING: self.nodes.planner,
            Lifecycle.PLAN_VALIDATION: self.nodes.plan_validator,
            Lifecycle.EXECUTING: self.nodes.executor,
            Lifecycle.STEP_VALIDATION: self.nodes.step_validator,
            Lifecycle.REPLANNING: self.nodes.replanner,
            Lifecycle.GOAL_VALIDATION: self.nodes.goal_validator,
            Lifecycle.ESCALATED: self._pause,
        }
        await self._checkpoint()
        for _ in range(64):
            self.os.kill_switch.assert_alive()
            if self.state.cancelled:
                self.state = self.state.model_copy(
                    update={
                        "lifecycle": Lifecycle.COMPLETED,
                        "result": AgentResult(status=TerminalStatus.CANCELLED, goal_satisfied=False),
                    }
                )
                break
            if self.state.lifecycle is Lifecycle.COMPLETED:
                break
            if self.state.replan_count > self.state.max_replans:
                raise NonConvergingPlanError("non-converging plan")
            handler = handlers.get(self.state.lifecycle)
            if handler is None:
                raise NonConvergingPlanError(f"no handler for {self.state.lifecycle}")
            self._apply(self.state.lifecycle, await handler(self.state))
            await self._checkpoint()
        else:
            raise NonConvergingPlanError("transition budget exhausted")
        fin = await self.nodes.finalizer(self.state)
        if "result" in fin:
            self.state = self.state.model_copy(update={"result": fin["result"]})
        if self.state.result is None:
            self.state = self.state.model_copy(
                update={
                    "result": AgentResult(
                        status=TerminalStatus.FAILED_PERMANENTLY,
                        goal_satisfied=False,
                    )
                }
            )
        return self.state.result

    async def _pause(self, state: AgentState) -> dict[str, Any]:
        return {
            "lifecycle": Lifecycle.COMPLETED,
            "result": AgentResult(status=TerminalStatus.APPROVAL_REQUIRED, goal_satisfied=False),
        }
