from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Protocol
from uuid import uuid4

from agent_kernel.contracts.plan import Plan, PlanStep
from agent_kernel.contracts.result import AgentResult
from agent_kernel.contracts.task import AgentTaskContract
from agent_kernel.errors import InvalidInputError, NonConvergingPlanError
from agent_kernel.lifecycle import Lifecycle, TerminalStatus, assert_transition
from agent_kernel.state import AgentState

NodeFn = Callable[[AgentState], Awaitable[dict[str, Any]]]


class NodeSet(Protocol):
    async def intake(self, state: AgentState) -> dict[str, Any]: ...

    async def goal_builder(self, state: AgentState) -> dict[str, Any]: ...

    async def planner(self, state: AgentState) -> dict[str, Any]: ...

    async def plan_validator(self, state: AgentState) -> dict[str, Any]: ...

    async def executor(self, state: AgentState) -> dict[str, Any]: ...

    async def step_validator(self, state: AgentState) -> dict[str, Any]: ...

    async def goal_validator(self, state: AgentState) -> dict[str, Any]: ...

    async def finalizer(self, state: AgentState) -> dict[str, Any]: ...


def _now() -> datetime:
    return datetime.now(timezone.utc)


class HappyPathNodes:
    """Deterministic test/default nodes. Domain agents replace these."""

    async def intake(self, state: AgentState) -> dict[str, Any]:
        if state.task is None:
            raise InvalidInputError("AgentTaskContract required")
        return {"lifecycle": Lifecycle.CONTRACTED}

    async def goal_builder(self, state: AgentState) -> dict[str, Any]:
        assert state.task is not None
        if not state.task.goal.success_criteria:
            raise InvalidInputError("success_criteria required")
        return {"lifecycle": Lifecycle.PLANNING}

    async def planner(self, state: AgentState) -> dict[str, Any]:
        assert state.task is not None
        criteria = state.task.goal.success_criteria
        steps = [
            PlanStep(
                id=f"step_{i}",
                objective=c,
                capability="domain",
                validator="goal",
            )
            for i, c in enumerate(criteria, start=1)
        ]
        plan = Plan(
            plan_id=str(uuid4()),
            version=1,
            goal_coverage={c: [s.id] for c, s in zip(criteria, steps, strict=True)},
            steps=steps,
        )
        return {"plan": plan, "lifecycle": Lifecycle.PLAN_VALIDATION}

    async def plan_validator(self, state: AgentState) -> dict[str, Any]:
        if state.plan is None or not state.plan.is_acyclic():
            return {"lifecycle": Lifecycle.PLANNING}
        return {"lifecycle": Lifecycle.EXECUTING}

    async def executor(self, state: AgentState) -> dict[str, Any]:
        results = {step.id: {"ok": True} for step in (state.plan.steps if state.plan else [])}
        return {"step_results": results, "lifecycle": Lifecycle.STEP_VALIDATION}

    async def step_validator(self, state: AgentState) -> dict[str, Any]:
        return {"lifecycle": Lifecycle.GOAL_VALIDATION}

    async def goal_validator(self, state: AgentState) -> dict[str, Any]:
        return {"lifecycle": Lifecycle.COMPLETED}

    async def finalizer(self, state: AgentState) -> dict[str, Any]:
        return {
            "result": AgentResult(status=TerminalStatus.SUCCEEDED, goal_satisfied=True),
        }


@dataclass
class Agent:
    """Reusable agent *type*. Holds ports and node implementations — not run state.

    100 concurrent executions: call ``spawn()`` 100 times (100 instances).
    """

    name: str
    nodes: NodeSet = field(default_factory=HappyPathNodes)
    ports: dict[str, Any] = field(default_factory=dict)

    def spawn(self) -> AgentRun:
        return AgentRun(name=self.name, nodes=self.nodes, ports=self.ports)

    async def execute(self, task: AgentTaskContract) -> AgentResult:
        """Always runs on a fresh instance. Safe to call concurrently on one Agent type."""
        return await self.spawn().execute(task)


@dataclass
class AgentRun:
    """One isolated execution. Do not reuse across tasks."""

    name: str
    nodes: NodeSet
    ports: dict[str, Any]
    run_id: str = field(default_factory=lambda: str(uuid4()))
    state: AgentState = field(default_factory=AgentState)

    def _apply(self, current: Lifecycle, updates: dict[str, Any]) -> None:
        nxt = updates.get("lifecycle")
        if nxt is not None and nxt != current:
            assert_transition(current, nxt)
        self.state = self.state.model_copy(update=updates)

    async def execute(self, task: AgentTaskContract) -> AgentResult:
        self.state = AgentState(task=task, lifecycle=Lifecycle.RECEIVED)
        sequence: list[tuple[Lifecycle, Callable[[AgentState], Awaitable[dict[str, Any]]]]] = [
            (Lifecycle.RECEIVED, self.nodes.intake),
            (Lifecycle.CONTRACTED, self.nodes.goal_builder),
            (Lifecycle.PLANNING, self.nodes.planner),
            (Lifecycle.PLAN_VALIDATION, self.nodes.plan_validator),
            (Lifecycle.EXECUTING, self.nodes.executor),
            (Lifecycle.STEP_VALIDATION, self.nodes.step_validator),
            (Lifecycle.GOAL_VALIDATION, self.nodes.goal_validator),
        ]
        steps = 0
        for expected, node in sequence:
            if self.state.lifecycle != expected:
                raise NonConvergingPlanError(
                    f"{self.name} run {self.run_id} expected {expected}, got {self.state.lifecycle}"
                )
            self._apply(self.state.lifecycle, await node(self.state))
            steps += 1
            limit = task.constraints.max_steps
            if limit is not None and steps > limit:
                break
        self._apply(self.state.lifecycle, await self.nodes.finalizer(self.state))
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
