from __future__ import annotations

from enum import StrEnum


class Lifecycle(StrEnum):
    RECEIVED = "Received"
    CONTRACTED = "Contracted"
    PLANNING = "Planning"
    PLAN_VALIDATION = "PlanValidation"
    EXECUTING = "Executing"
    STEP_VALIDATION = "StepValidation"
    REPLANNING = "Replanning"
    GOAL_VALIDATION = "GoalValidation"
    ESCALATED = "Escalated"
    COMPLETED = "Completed"


class TerminalStatus(StrEnum):
    SUCCEEDED = "Succeeded"
    SUCCEEDED_WITH_WARNINGS = "SucceededWithWarnings"
    PARTIALLY_SUCCEEDED = "PartiallySucceeded"
    BLOCKED = "Blocked"
    APPROVAL_REQUIRED = "ApprovalRequired"
    BUDGET_EXHAUSTED = "BudgetExhausted"
    DEADLINE_EXCEEDED = "DeadlineExceeded"
    POLICY_DENIED = "PolicyDenied"
    CANCELLED = "Cancelled"
    FAILED_RECOVERABLY = "FailedRecoverably"
    FAILED_PERMANENTLY = "FailedPermanently"


ALLOWED_TRANSITIONS: dict[Lifecycle, frozenset[Lifecycle]] = {
    Lifecycle.RECEIVED: frozenset({Lifecycle.CONTRACTED}),
    Lifecycle.CONTRACTED: frozenset({Lifecycle.PLANNING}),
    Lifecycle.PLANNING: frozenset({Lifecycle.PLAN_VALIDATION}),
    Lifecycle.PLAN_VALIDATION: frozenset({Lifecycle.EXECUTING, Lifecycle.PLANNING}),
    Lifecycle.EXECUTING: frozenset({Lifecycle.STEP_VALIDATION}),
    Lifecycle.STEP_VALIDATION: frozenset(
        {Lifecycle.EXECUTING, Lifecycle.REPLANNING, Lifecycle.GOAL_VALIDATION}
    ),
    Lifecycle.REPLANNING: frozenset({Lifecycle.PLAN_VALIDATION}),
    Lifecycle.GOAL_VALIDATION: frozenset(
        {Lifecycle.COMPLETED, Lifecycle.REPLANNING, Lifecycle.ESCALATED}
    ),
    Lifecycle.ESCALATED: frozenset({Lifecycle.EXECUTING, Lifecycle.COMPLETED}),
    Lifecycle.COMPLETED: frozenset(),
}


class IllegalTransition(ValueError):
    pass


def assert_transition(current: Lifecycle, nxt: Lifecycle) -> None:
    if nxt not in ALLOWED_TRANSITIONS[current]:
        raise IllegalTransition(f"{current} → {nxt} is not allowed")
