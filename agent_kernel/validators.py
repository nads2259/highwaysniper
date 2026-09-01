from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from agent_kernel.contracts.plan import Plan
from agent_kernel.contracts.result import AgentResult, Claim
from agent_kernel.contracts.task import AgentTaskContract
from agent_kernel.state import AgentState


@dataclass
class ValidationReport:
    ok: bool
    level: str
    details: list[str] = field(default_factory=list)
    confidence: float = 1.0


class IndependentValidator(Protocol):
    async def validate(self, state: AgentState) -> ValidationReport: ...


async def input_validation(task: AgentTaskContract, supported: set[str]) -> ValidationReport:
    details: list[str] = []
    if not task.goal.success_criteria:
        details.append("missing success_criteria")
    if not task.execution.idempotency_key:
        details.append("missing idempotency_key")
    if task.agent.capability not in supported:
        details.append("unsupported capability")
    return ValidationReport(ok=not details, level="input", details=details)


async def plan_validation(state: AgentState) -> ValidationReport:
    from agent_kernel.plan_validate import validate_plan

    assert state.task and state.plan
    report = validate_plan(state.plan, state.task)
    return ValidationReport(ok=report.ok, level="plan", details=report.errors)


async def step_validation(state: AgentState, step_id: str) -> ValidationReport:
    envelope = state.step_results.get(step_id)
    details: list[str] = []
    if not envelope:
        details.append("missing envelope")
    elif not envelope.get("ok"):
        details.append("step not ok")
    elif not envelope.get("evidence_refs"):
        details.append("missing evidence")
    return ValidationReport(ok=not details, level="step", details=details)


async def goal_validation(state: AgentState) -> ValidationReport:
    assert state.task
    details: list[str] = []
    for criterion in state.task.goal.success_criteria:
        covered = False
        if state.plan:
            for sid in state.plan.goal_coverage.get(criterion, []):
                if sid in state.validated_steps:
                    covered = True
        if not covered:
            details.append(f"criterion unsatisfied: {criterion}")
    return ValidationReport(ok=not details, level="goal", details=details, confidence=1.0 if not details else 0.0)


def claims_from_steps(state: AgentState) -> list[Claim]:
    claims: list[Claim] = []
    for sid, env in state.step_results.items():
        if env.get("ok"):
            claims.append(
                Claim(
                    statement=str(env.get("statement", sid)),
                    evidence_refs=list(env.get("evidence_refs", [])),
                    validator_results=list(env.get("validator_results", [])),
                )
            )
    return claims
