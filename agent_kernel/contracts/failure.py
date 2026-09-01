from __future__ import annotations

from enum import StrEnum


class FailureCategory(StrEnum):
    INVALID_INPUT = "invalid_input"
    UNSUPPORTED_CAPABILITY = "unsupported_capability"
    AMBIGUOUS_GOAL = "ambiguous_goal"
    POLICY_DENIAL = "policy_denial"
    APPROVAL_REQUIRED = "approval_required"
    BUDGET_EXHAUSTED = "budget_exhausted"
    TRANSIENT_DEPENDENCY = "transient_dependency"
    PERMANENT_DEPENDENCY = "permanent_dependency"
    MODEL_REFUSAL = "model_refusal"
    MODEL_MALFORMED_OUTPUT = "model_malformed_output"
    TOOL_CONTRACT_VIOLATION = "tool_contract_violation"
    VALIDATION_FAILURE = "validation_failure"
    EVIDENCE_INSUFFICIENCY = "evidence_insufficiency"
    STATE_CONFLICT = "state_conflict"
    LEASE_LOSS = "lease_loss"
    DEADLINE_EXCEEDED = "deadline_exceeded"
    SECURITY_INCIDENT = "security_incident"
    NON_CONVERGING_PLAN = "non_converging_plan"
    HUMAN_INTERVENTION_REQUIRED = "human_intervention_required"
