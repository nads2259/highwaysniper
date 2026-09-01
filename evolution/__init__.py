from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ImprovementProposal:
    kind: str
    payload: dict[str, Any]
    approved: bool = False


FORBIDDEN_DIRECT = frozenset(
    {
        "mutate_production_prompts",
        "grant_self_permissions",
        "install_unverified_tool",
        "change_acceptance_thresholds",
        "promote_own_release",
        "alter_audit_evidence",
        "write_hypothesis_to_semantic_memory",
    }
)


class ImprovementPipeline:
    def __init__(self) -> None:
        self.proposals: list[ImprovementProposal] = []

    def propose(self, kind: str, payload: dict[str, Any]) -> ImprovementProposal:
        if kind in FORBIDDEN_DIRECT:
            raise PermissionError(kind)
        prop = ImprovementProposal(kind=kind, payload=payload)
        self.proposals.append(prop)
        return prop

    def promote(self, prop: ImprovementProposal, *, signed: bool, canary_ok: bool) -> None:
        if not signed or not canary_ok:
            raise PermissionError("unsigned or canary failed")
        prop.approved = True
