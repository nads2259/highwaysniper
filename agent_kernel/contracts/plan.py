from __future__ import annotations

from pydantic import BaseModel, Field


class PlanStep(BaseModel):
    id: str
    objective: str
    dependencies: list[str] = Field(default_factory=list)
    capability: str
    validator: str
    retry_class: str = "safe"
    estimated_cost: float = 0.0
    fallback_id: str | None = None
    compensation_capability: str | None = None
    side_effect_class: str = "none"
    approval_required: bool = False
    bounded: bool = True


class Plan(BaseModel):
    plan_id: str
    version: int
    goal_coverage: dict[str, list[str]] = Field(default_factory=dict)
    steps: list[PlanStep] = Field(default_factory=list)

    def step_ids(self) -> set[str]:
        return {step.id for step in self.steps}

    def by_id(self) -> dict[str, PlanStep]:
        return {step.id: step for step in self.steps}

    def is_acyclic(self) -> bool:
        ids = self.step_ids()
        incoming: dict[str, set[str]] = {sid: set() for sid in ids}
        for step in self.steps:
            for dep in step.dependencies:
                if dep not in ids:
                    return False
                incoming[step.id].add(dep)
        ready = [sid for sid, deps in incoming.items() if not deps]
        seen = 0
        while ready:
            node = ready.pop()
            seen += 1
            for step in self.steps:
                if node in incoming[step.id]:
                    incoming[step.id].remove(node)
                    if not incoming[step.id]:
                        ready.append(step.id)
        return seen == len(ids)

    def ready_steps(self, completed: set[str]) -> list[PlanStep]:
        return [
            step
            for step in self.steps
            if step.id not in completed and set(step.dependencies) <= completed
        ]

    def independent_branches(self) -> list[list[str]]:
        roots = [s.id for s in self.steps if not s.dependencies]
        return [[r] for r in roots]
