from __future__ import annotations

from pydantic import BaseModel, Field

from agent_kernel.lifecycle import TerminalStatus


class Claim(BaseModel):
    statement: str
    evidence_refs: list[str] = Field(default_factory=list)
    validator_results: list[str] = Field(default_factory=list)


class ExecutionSummary(BaseModel):
    plan_version: int = 0
    attempts: int = 0
    cost: float = 0.0
    duration_seconds: float = 0.0


class AgentResult(BaseModel):
    status: TerminalStatus
    goal_satisfied: bool
    result: object | None = None
    claims: list[Claim] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)
    unresolved_items: list[str] = Field(default_factory=list)
    execution_summary: ExecutionSummary = Field(default_factory=ExecutionSummary)
