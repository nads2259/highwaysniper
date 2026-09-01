"""Compile the durable graph. Wire nodes; do not run an unconstrained loop."""

from __future__ import annotations

NODE_ORDER = (
    "intake",
    "goal_builder",
    "context_builder",
    "planner",
    "plan_validator",
    "scheduler",
    "executor",
    "step_validator",
    "goal_validator",
    "replanner",
    "finalizer",
)


def build_graph() -> dict[str, tuple[str, ...]]:
    """Return declared edges for the lifecycle. Runtime binds these to LangGraph or a worker."""

    return {
        "intake": ("goal_builder",),
        "goal_builder": ("context_builder",),
        "context_builder": ("planner",),
        "planner": ("plan_validator",),
        "plan_validator": ("scheduler", "planner"),
        "scheduler": ("executor",),
        "executor": ("step_validator",),
        "step_validator": ("executor", "replanner", "goal_validator"),
        "replanner": ("plan_validator",),
        "goal_validator": ("finalizer", "replanner"),
        "finalizer": (),
    }
