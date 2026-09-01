from __future__ import annotations

from enum import StrEnum

from agent_kernel.contracts.failure import FailureCategory
from agent_kernel.contracts.failure_envelope import FailureEnvelope
from agent_kernel.lifecycle import TerminalStatus


class RecoveryAction(StrEnum):
    DELAYED_RETRY = "delayed_retry"
    PROVIDER_FALLBACK = "provider_fallback"
    REPAIR_ONCE = "repair_once"
    RETURN_TO_PLANNER = "return_to_planner"
    ALTERNATIVE_CAPABILITY = "alternative_capability"
    REPLAN_ON_GAPS = "replan_on_gaps"
    STOP = "stop"
    DURABLE_PAUSE = "durable_pause"
    STOP_STALE_WORKER = "stop_stale_worker"
    PARTIAL_OR_TERMINATE = "partial_or_terminate"
    RECONCILE_BEFORE_RETRY = "reconcile_before_retry"
    QUARANTINE_AND_ESCALATE = "quarantine_and_escalate"


_MATRIX: dict[FailureCategory, RecoveryAction] = {
    FailureCategory.TRANSIENT_DEPENDENCY: RecoveryAction.DELAYED_RETRY,
    FailureCategory.MODEL_MALFORMED_OUTPUT: RecoveryAction.REPAIR_ONCE,
    FailureCategory.MODEL_REFUSAL: RecoveryAction.PROVIDER_FALLBACK,
    FailureCategory.AMBIGUOUS_GOAL: RecoveryAction.RETURN_TO_PLANNER,
    FailureCategory.UNSUPPORTED_CAPABILITY: RecoveryAction.ALTERNATIVE_CAPABILITY,
    FailureCategory.VALIDATION_FAILURE: RecoveryAction.RETURN_TO_PLANNER,
    FailureCategory.EVIDENCE_INSUFFICIENCY: RecoveryAction.REPLAN_ON_GAPS,
    FailureCategory.POLICY_DENIAL: RecoveryAction.STOP,
    FailureCategory.APPROVAL_REQUIRED: RecoveryAction.DURABLE_PAUSE,
    FailureCategory.LEASE_LOSS: RecoveryAction.STOP_STALE_WORKER,
    FailureCategory.BUDGET_EXHAUSTED: RecoveryAction.PARTIAL_OR_TERMINATE,
    FailureCategory.SECURITY_INCIDENT: RecoveryAction.QUARANTINE_AND_ESCALATE,
    FailureCategory.NON_CONVERGING_PLAN: RecoveryAction.STOP,
    FailureCategory.DEADLINE_EXCEEDED: RecoveryAction.PARTIAL_OR_TERMINATE,
    FailureCategory.PERMANENT_DEPENDENCY: RecoveryAction.ALTERNATIVE_CAPABILITY,
    FailureCategory.STATE_CONFLICT: RecoveryAction.STOP_STALE_WORKER,
    FailureCategory.TOOL_CONTRACT_VIOLATION: RecoveryAction.RECONCILE_BEFORE_RETRY,
    FailureCategory.INVALID_INPUT: RecoveryAction.STOP,
    FailureCategory.HUMAN_INTERVENTION_REQUIRED: RecoveryAction.DURABLE_PAUSE,
}

_TERMINAL: dict[RecoveryAction, TerminalStatus] = {
    RecoveryAction.STOP: TerminalStatus.FAILED_PERMANENTLY,
    RecoveryAction.STOP_STALE_WORKER: TerminalStatus.FAILED_RECOVERABLY,
    RecoveryAction.DURABLE_PAUSE: TerminalStatus.APPROVAL_REQUIRED,
    RecoveryAction.PARTIAL_OR_TERMINATE: TerminalStatus.PARTIALLY_SUCCEEDED,
    RecoveryAction.QUARANTINE_AND_ESCALATE: TerminalStatus.FAILED_PERMANENTLY,
}


def decide_recovery(envelope: FailureEnvelope) -> RecoveryAction:
    return _MATRIX[envelope.category]


def terminal_for(action: RecoveryAction) -> TerminalStatus | None:
    return _TERMINAL.get(action)
