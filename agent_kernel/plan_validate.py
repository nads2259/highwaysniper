from __future__ import annotations

from dataclasses import dataclass, field

from agent_kernel.contracts.plan import Plan, PlanStep
from agent_kernel.contracts.task import AgentTaskContract


@dataclass
class PlanValidationReport:
    ok: bool
    errors: list[str] = field(default_factory=list)
    independent_branches: list[list[str]] = field(default_factory=list)


def validate_plan(
    plan: Plan,
    task: AgentTaskContract,
    available_capabilities: set[str] | None = None,
) -> PlanValidationReport:
    errors: list[str] = []
    ids = plan.step_ids()
    if not plan.is_acyclic():
        errors.append("dependencies are not a valid DAG")
    for criterion in task.goal.success_criteria:
        covered = plan.goal_coverage.get(criterion, [])
        if not covered or any(sid not in ids for sid in covered):
            errors.append(f"success criterion uncovered: {criterion}")
    if available_capabilities:
        for step in plan.steps:
            if step.capability not in available_capabilities:
                errors.append(f"capability unavailable: {step.capability}")
    budget = task.constraints.max_cost_usd
    if budget is not None:
        estimate = sum(s.estimated_cost for s in plan.steps)
        if estimate > budget:
            errors.append(f"estimated cost {estimate} exceeds budget {budget}")
    for step in plan.steps:
        if not step.bounded:
            errors.append(f"unbounded task: {step.id}")
        if not step.validator:
            errors.append(f"missing validator: {step.id}")
        if step.side_effect_class not in {"none", "idempotent", "compensatable", "approval"}:
            errors.append(f"unknown side_effect_class: {step.id}")
        if step.side_effect_class in {"compensatable", "approval"} and not (
            step.compensation_capability or step.approval_required
        ):
            errors.append(f"side effect lacks compensation/approval: {step.id}")
        if step.fallback_id and step.fallback_id not in ids and step.fallback_id != "replan":
            errors.append(f"missing fallback: {step.id}")
        for dep in step.dependencies:
            if dep not in ids:
                errors.append(f"missing input producer {dep} for {step.id}")
    if not plan.independent_branches() and plan.steps:
        errors.append("no identifiable concurrent branches")
    return PlanValidationReport(
        ok=not errors,
        errors=errors,
        independent_branches=plan.independent_branches(),
    )


def compile_plan(plan: Plan) -> list[PlanStep]:
    """Abstract plan → executable order (Kahn)."""
    done: set[str] = set()
    order: list[PlanStep] = []
    by_id = plan.by_id()
    while len(order) < len(plan.steps):
        ready = [s for s in plan.steps if s.id not in done and set(s.dependencies) <= done]
        if not ready:
            break
        ready.sort(key=lambda s: s.id)
        step = ready[0]
        order.append(step)
        done.add(step.id)
    return order
