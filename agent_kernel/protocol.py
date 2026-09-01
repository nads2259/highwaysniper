"""Canonical internal protocol. External systems attach through adapters only."""

CANONICAL_TYPES = (
    "AgentTask",
    "AgentResult",
    "AgentEvent",
    "AgentManifest",
    "CapabilityDescriptor",
    "ToolRequest",
    "ToolResult",
    "Artifact",
    "Evidence",
    "ApprovalRequest",
    "Checkpoint",
    "MemoryRecord",
    "FailureEnvelope",
    "RuntimeBundle",
    "AuthorityGrant",
)

ADAPTER_TARGETS = (
    "rest",
    "grpc",
    "event_queue",
    "langgraph",
    "mcp",
    "a2a",
    "agntcy",
    "local_process",
)
