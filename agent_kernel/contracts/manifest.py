from __future__ import annotations

from pydantic import BaseModel, Field


class CapabilityDescriptor(BaseModel):
    id: str
    version: str
    summary: str
    input_schema: str
    output_schema: str


class AgentManifest(BaseModel):
    id: str
    version: str
    title: str
    capability: CapabilityDescriptor
    graph_version: int = 1
    task_contract_version: int = 1
    result_contract_version: int = 1
    owns: list[str] = Field(
        default_factory=lambda: [
            "domain_reasoning",
            "goal_decomposition",
            "internal_execution_graph",
            "domain_validation",
            "local_working_memory",
            "result_and_evidence_contract",
            "recovery_within_limits",
        ]
    )
    does_not_own: list[str] = Field(
        default_factory=lambda: [
            "authentication",
            "tenant_isolation",
            "global_authorization",
            "secrets",
            "cross_agent_scheduling",
            "global_concurrency",
            "event_ledger_storage",
            "tool_sandbox_runtime",
            "human_approval_routing",
            "final_mission_acceptance",
        ]
    )
