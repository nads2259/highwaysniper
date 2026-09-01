from __future__ import annotations

from dataclasses import dataclass
from typing import Any

EVAL_FAMILIES = (
    "contract",
    "capability",
    "golden_task",
    "grounding",
    "goal_completion",
    "adversarial",
    "recovery",
    "replay",
    "concurrency",
    "long_duration",
    "model_swap",
    "tool_swap",
    "cost",
    "drift",
    "human",
)


@dataclass
class EvalResult:
    family: str
    passed: bool
    score: float
    security_ok: bool = True
    cost_ok: bool = True
    tail_latency_ok: bool = True
    critical_ok: bool = True


def release_gate(results: list[EvalResult]) -> bool:
    if not results:
        return False
    if any(not r.passed for r in results):
        return False
    if any(not r.security_ok or not r.cost_ok or not r.tail_latency_ok or not r.critical_ok for r in results):
        return False
    return True
