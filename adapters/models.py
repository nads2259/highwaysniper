from __future__ import annotations

from agent_kernel.contracts.model import ModelRequest, ModelResponse, ToolRequest, ToolResult
from agent_kernel.errors import SecurityError
from agent_os import Sandbox


class LocalChatModel:
    async def generate(self, request: ModelRequest) -> ModelResponse:
        return ModelResponse(content="ok", usage_tokens=1)


class LocalEmbedder:
    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(t))] for t in texts]


class SandboxToolAdapter:
    def __init__(self, sandbox: Sandbox | None = None) -> None:
        self.sandbox = sandbox or Sandbox()
        self.registry: dict[str, dict] = {}

    def register(self, name: str, *, digest: str, publisher: str, side_effect_class: str, revoked: bool = False) -> None:
        self.registry[name] = {
            "digest": digest,
            "publisher": publisher,
            "side_effect_class": side_effect_class,
            "revoked": revoked,
        }

    async def execute(self, request: ToolRequest) -> ToolResult:
        meta = self.registry.get(request.name)
        if meta is None:
            raise SecurityError("unregistered tool")
        if meta["revoked"]:
            raise SecurityError("revoked tool")
        payload = await self.sandbox.run(request.name if request.name in self.sandbox.allowed else "echo", request.arguments)
        return ToolResult(ok=True, payload=payload, receipt_id=request.idempotency_key)
