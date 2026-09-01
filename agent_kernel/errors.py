from __future__ import annotations

from agent_kernel.contracts.failure import FailureCategory
from agent_kernel.contracts.failure_envelope import FailureEnvelope


class AgentError(Exception):
    category: FailureCategory = FailureCategory.VALIDATION_FAILURE
    retryable: bool = False
    safe_to_repeat: bool = False
    compensation_required: bool = False
    code: str = "agent_error"

    def to_envelope(self, message: str | None = None) -> FailureEnvelope:
        return FailureEnvelope(
            code=self.code,
            category=self.category,
            message=message or str(self),
            retryable=self.retryable,
            safe_to_repeat=self.safe_to_repeat,
            compensation_required=self.compensation_required,
        )


class ContractError(AgentError):
    code = "contract_error"


class InvalidInputError(ContractError):
    category = FailureCategory.INVALID_INPUT
    code = "invalid_input"


class UnsupportedCapabilityError(ContractError):
    category = FailureCategory.UNSUPPORTED_CAPABILITY
    code = "unsupported_capability"


class PlanningError(AgentError):
    code = "planning_error"


class InfeasiblePlanError(PlanningError):
    category = FailureCategory.VALIDATION_FAILURE
    code = "infeasible_plan"


class NonConvergingPlanError(PlanningError):
    category = FailureCategory.NON_CONVERGING_PLAN
    code = "non_converging_plan"


class ExecutionError(AgentError):
    code = "execution_error"


class TransientDependencyError(ExecutionError):
    category = FailureCategory.TRANSIENT_DEPENDENCY
    retryable = True
    safe_to_repeat = True
    code = "transient_dependency"


class PermanentDependencyError(ExecutionError):
    category = FailureCategory.PERMANENT_DEPENDENCY
    code = "permanent_dependency"


class TimeoutError(ExecutionError):
    category = FailureCategory.DEADLINE_EXCEEDED
    retryable = True
    code = "timeout"


class LeaseLostError(ExecutionError):
    category = FailureCategory.LEASE_LOSS
    code = "lease_lost"


class ValidationFailedError(AgentError):
    category = FailureCategory.VALIDATION_FAILURE
    code = "validation_failed"


class SchemaValidationError(ValidationFailedError):
    code = "schema_validation"


class EvidenceInsufficientError(ValidationFailedError):
    category = FailureCategory.EVIDENCE_INSUFFICIENCY
    code = "evidence_insufficient"


class GoalNotSatisfiedError(ValidationFailedError):
    category = FailureCategory.VALIDATION_FAILURE
    code = "goal_not_satisfied"


class PolicyError(AgentError):
    category = FailureCategory.POLICY_DENIAL
    code = "policy_error"


class AuthorizationDeniedError(PolicyError):
    code = "authorization_denied"


class ApprovalRequiredError(PolicyError):
    category = FailureCategory.APPROVAL_REQUIRED
    code = "approval_required"


class BudgetError(AgentError):
    category = FailureCategory.BUDGET_EXHAUSTED
    code = "budget_exhausted"


class SecurityError(AgentError):
    category = FailureCategory.SECURITY_INCIDENT
    code = "security_incident"
