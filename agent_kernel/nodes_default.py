from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from typing import Any
from uuid import uuid4

from agent_kernel.context_compiler import compile_context
from agent_kernel.contracts.plan import Plan, PlanStep
from agent_kernel.contracts.result import AgentResult, ExecutionSummary
from agent_kernel.errors import InvalidInputError, NonConvergingPlanError
from agent_kernel.lifecycle import Lifecycle, TerminalStatus
from agent_kernel.plan_validate import compile_plan, validate_plan
from agent_kernel.scheduler import run_dag
from agent_kernel.state import AgentState
from agent_kernel.validators import goal_validation, input_validation, step_validation
from agent_os import AgentOS, Sandbox


class KernelNodes:
    """Deterministic shell nodes. Domain agents inject planner/executor intelligence here."""

    def __init__(self, os: AgentOS | None = None) -> None:
        self.os = os or AgentOS()
        self.supported = set(self.os.sandbox.allowed) | {"domain", "agent_package_authoring", "echo"}

    async def intake(self, state: AgentState) -> dict[str, Any]:
        if state.task is None:
            raise InvalidInputError("AgentTaskContract required")
        self.os.kill_switch.assert_alive()
        report = await input_validation(state.task, self.supported)
        if not report.ok:
            raise InvalidInputError(";".join(report.details))
        await self.os.ledger.append({"kind": "intake", "task_id": state.task.task_id})
        return {"lifecycle": Lifecycle.CONTRACTED}

    async def goal_builder(self, state: AgentState) -> dict[str, Any]:
        assert state.task is not None
        ctx = compile_context(
            trusted_instructions=[state.task.goal.statement],
            sources=[(str(v), f"input.{k}", "1") for k, v in state.task.inputs.items()]
            or [("none", "empty", "0")],
        )
        return {"context": ctx, "lifecycle": Lifecycle.PLANNING}

    async def planner(self, state: AgentState) -> dict[str, Any]:
        assert state.task is not None
        criteria = state.task.goal.success_criteria
        steps = [
            PlanStep(
                id=f"step_{i}",
                objective=c,
                capability="domain",
                validator="goal",
                estimated_cost=0.01,
                fallback_id="replan",
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
        assert state.task and state.plan
        report = validate_plan(state.plan, state.task, available_capabilities=self.supported)
        if not report.ok:
            return {"lifecycle": Lifecycle.PLANNING, "replan_count": state.replan_count + 1}
        compiled = [s.id for s in compile_plan(state.plan)]
        return {"compiled_plan": compiled, "lifecycle": Lifecycle.EXECUTING}

    async def executor(self, state: AgentState) -> dict[str, Any]:
        assert state.plan and state.task
        sandbox = self.os.sandbox

        async def _step(step: PlanStep, lease) -> dict[str, Any]:
            payload = await sandbox.run("domain", {"objective": step.objective, "lease": lease.fencing_token})
            evidence_id = sha256(f"{step.id}:{lease.fencing_token}".encode()).hexdigest()[:16]
            await self.os.ledger.append({"kind": "tool", "step": step.id, "receipt": evidence_id})
            return {
                "ok": True,
                "statement": step.objective,
                "evidence_refs": [evidence_id],
                "validator_results": [step.validator],
                "payload": payload,
            }

        envelopes = await run_dag(
            state.plan,
            _step,
            max_parallel=state.task.constraints.max_parallel_tasks,
            lease_port=self.os.leases,
        )
        return {"step_results": envelopes, "lifecycle": Lifecycle.STEP_VALIDATION}

    async def step_validator(self, state: AgentState) -> dict[str, Any]:
        validated: set[str] = set()
        for sid in state.step_results:
            report = await step_validation(state, sid)
            if report.ok:
                validated.add(sid)
        if state.plan and len(validated) < len(state.plan.steps):
            return {"validated_steps": validated, "lifecycle": Lifecycle.REPLANNING}
        return {"validated_steps": validated, "lifecycle": Lifecycle.GOAL_VALIDATION}

    async def replanner(self, state: AgentState) -> dict[str, Any]:
        if state.replan_count >= state.max_replans:
            raise NonConvergingPlanError("max replans")
        return {"replan_count": state.replan_count + 1, "lifecycle": Lifecycle.PLAN_VALIDATION}

    async def goal_validator(self, state: AgentState) -> dict[str, Any]:
        report = await goal_validation(state)
        if report.ok:
            return {"lifecycle": Lifecycle.COMPLETED}
        if state.paused_for_approval:
            return {"lifecycle": Lifecycle.ESCALATED}
        return {"lifecycle": Lifecycle.REPLANNING, "replan_count": state.replan_count + 1}

    async def finalizer(self, state: AgentState) -> dict[str, Any]:
        from agent_kernel.validators import claims_from_steps

        satisfied = state.lifecycle == Lifecycle.COMPLETED
        status = TerminalStatus.SUCCEEDED if satisfied else TerminalStatus.PARTIALLY_SUCCEEDED
        return {
            "result": AgentResult(
                status=status,
                goal_satisfied=satisfied,
                claims=claims_from_steps(state),
                execution_summary=ExecutionSummary(plan_version=state.plan.version if state.plan else 0),
            )
        }
