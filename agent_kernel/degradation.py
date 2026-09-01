from __future__ import annotations

from agent_kernel.lifecycle import TerminalStatus
from agent_kernel.state import AgentState


def degrade(state: AgentState, reason: str) -> TerminalStatus:
    mapping = {
        "preferred_model_gone": TerminalStatus.SUCCEEDED_WITH_WARNINGS,
        "validator_down": TerminalStatus.SUCCEEDED_WITH_WARNINGS,
        "queue_redelivery": TerminalStatus.SUCCEEDED,
        "worker_crash_after_effect": TerminalStatus.FAILED_RECOVERABLY,
        "context_overflow": TerminalStatus.SUCCEEDED_WITH_WARNINGS,
        "human_timeout": TerminalStatus.BLOCKED,
        "cost_limit": TerminalStatus.BUDGET_EXHAUSTED,
        "malicious_tool": TerminalStatus.FAILED_PERMANENTLY,
        "evidence_store_down": TerminalStatus.SUCCEEDED_WITH_WARNINGS,
        "mid_run_release": TerminalStatus.SUCCEEDED_WITH_WARNINGS,
        "policy": TerminalStatus.POLICY_DENIED,
        "cancelled": TerminalStatus.CANCELLED,
        "deadline": TerminalStatus.DEADLINE_EXCEEDED,
        "approval": TerminalStatus.APPROVAL_REQUIRED,
    }
    return mapping.get(reason, TerminalStatus.FAILED_RECOVERABLY)


def never_false_success(status: TerminalStatus, goal_satisfied: bool) -> bool:
    if status is TerminalStatus.SUCCEEDED and not goal_satisfied:
        return False
    return True
