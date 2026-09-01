from __future__ import annotations

from dataclasses import dataclass

from evaluations import EvalResult, release_gate

STAGES = (
    "static_checks",
    "contract_compatibility",
    "unit_component",
    "graph_compilation",
    "prompt_evaluations",
    "model_matrix",
    "tool_conformance",
    "security_adversarial",
    "failure_recovery",
    "load_concurrency",
    "signed_runtime_bundle",
    "shadow_traffic",
    "canary",
    "progressive_rollout",
    "automated_rollback",
)


@dataclass
class ReleaseRecord:
    version: str
    signed: bool
    stages: tuple[str, ...]
    passed: bool


def run_release(version: str, evals: list[EvalResult], *, worsen_security: bool = False) -> ReleaseRecord:
    if worsen_security:
        return ReleaseRecord(version=version, signed=False, stages=STAGES, passed=False)
    ok = release_gate(evals)
    return ReleaseRecord(version=version, signed=ok, stages=STAGES, passed=ok)
