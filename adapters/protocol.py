"""Protocol adapters: canonical types at the center; MCP/A2A/AGNTCY/REST/gRPC at the edge."""

from __future__ import annotations

from typing import Any

from agent_kernel.contracts.manifest import AgentManifest
from agent_kernel.contracts.result import AgentResult
from agent_kernel.contracts.task import AgentTaskContract
from agent_kernel.protocol import ADAPTER_TARGETS, CANONICAL_TYPES


def encode_task(task: AgentTaskContract) -> dict[str, Any]:
    return task.model_dump(mode="json")


def decode_task(payload: dict[str, Any]) -> AgentTaskContract:
    return AgentTaskContract.model_validate(payload)


def encode_result(result: AgentResult) -> dict[str, Any]:
    return result.model_dump(mode="json")


class RestAdapter:
    def inbound(self, body: dict[str, Any]) -> AgentTaskContract:
        return decode_task(body)

    def outbound(self, result: AgentResult) -> dict[str, Any]:
        return encode_result(result)


class GrpcAdapter:
    """Canonical codec usable by a gRPC binding; domain never sees protobuf types."""

    def inbound(self, body: dict[str, Any]) -> AgentTaskContract:
        return decode_task(body)

    def outbound(self, result: AgentResult) -> dict[str, Any]:
        return encode_result(result)


class EventQueueAdapter:
    def inbound(self, message: dict[str, Any]) -> AgentTaskContract:
        return decode_task(message["task"])

    def outbound(self, result: AgentResult) -> dict[str, Any]:
        return {"result": encode_result(result)}


class McpAdapter:
    def tools_to_canonical(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        return {"capability": tool_name, "arguments": arguments}

    def never_trust_metadata(self, description: str) -> bool:
        return True


class A2AAdapter:
    def agent_card(self, manifest: AgentManifest) -> dict[str, Any]:
        return {
            "name": manifest.id,
            "version": manifest.version,
            "capabilities": [manifest.capability.id],
            "bindings": ["json"],
        }


class AgntcyAdapter:
    def identity_document(self, manifest: AgentManifest, registry_doc: dict[str, Any]) -> dict[str, Any]:
        return {**registry_doc, "manifest_id": manifest.id, "spec": "agntcy-compatible"}


class LocalProcessAdapter:
    def inbound(self, task: AgentTaskContract) -> AgentTaskContract:
        return task


class LangGraphAdapter:
    """Lifecycle graph spec. Canonical state machine is agent_kernel.runtime, not LangGraph types."""

    def graph_spec(self) -> dict[str, list[str]]:
        return {
            "Received": ["Contracted"],
            "Contracted": ["Planning"],
            "Planning": ["PlanValidation"],
            "PlanValidation": ["Executing", "Planning"],
            "Executing": ["StepValidation"],
            "StepValidation": ["Executing", "Replanning", "GoalValidation"],
            "Replanning": ["PlanValidation"],
            "GoalValidation": ["Completed", "Replanning", "Escalated"],
            "Escalated": ["Executing", "Completed"],
        }


def advertised_adapters() -> tuple[str, ...]:
    return ADAPTER_TARGETS


def advertised_types() -> tuple[str, ...]:
    return CANONICAL_TYPES
