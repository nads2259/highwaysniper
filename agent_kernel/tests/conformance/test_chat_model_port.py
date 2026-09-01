"""Behavioural conformance for ChatModelPort — LSP, not just matching method names."""

import asyncio

from agent_kernel.contracts.model import ModelRequest, ModelResponse
from agent_kernel.ports import ChatModelPort


class EchoModel:
    async def generate(self, request: ModelRequest) -> ModelResponse:
        last = request.messages[-1]["content"] if request.messages else ""
        return ModelResponse(content=last, usage_tokens=1)


def test_structured_and_usage() -> None:
    model: ChatModelPort = EchoModel()
    response = asyncio.run(
        model.generate(ModelRequest(role="planner", messages=[{"role": "user", "content": "ok"}]))
    )
    assert response.content == "ok"
    assert response.usage_tokens >= 0
    assert response.refusal is False
