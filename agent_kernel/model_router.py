"""Capability-based model selection. Never bind domain code to a brand name."""

from __future__ import annotations

from dataclasses import dataclass

from agent_kernel.contracts.runtime_bundle import ModelRequirement


@dataclass(frozen=True)
class ModelProfile:
    id: str
    roles: frozenset[str]
    capabilities: frozenset[str]
    cost_per_million: float
    p95_latency_ms: int
    regions: frozenset[str]
    fallback: str | None = None


def select_model(
    requirement: ModelRequirement,
    catalog: list[ModelProfile],
) -> ModelProfile:
    required = set(requirement.required)
    roles = set(requirement.roles)
    max_cost = float(requirement.constraints.get("maximum_cost_per_million_tokens", 10**9))
    max_p95 = int(requirement.constraints.get("maximum_p95_latency_ms", 10**9))
    regions = set(requirement.constraints.get("allowed_data_regions", []) or [])
    qualified: list[ModelProfile] = []
    for profile in catalog:
        if roles - profile.roles:
            continue
        if required - profile.capabilities:
            continue
        if profile.cost_per_million > max_cost:
            continue
        if profile.p95_latency_ms > max_p95:
            continue
        if regions and not (profile.regions & regions):
            continue
        qualified.append(profile)
    if not qualified:
        raise LookupError("no qualified model")
    qualified.sort(key=lambda p: (p.cost_per_million, p.p95_latency_ms))
    return qualified[0]
