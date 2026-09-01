from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CapabilityContract:
    capability: str
    preconditions: tuple[str, ...]
    postconditions: tuple[str, ...]
    invariants: tuple[str, ...]


def assert_pre(contract: CapabilityContract, facts: set[str]) -> None:
    missing = [p for p in contract.preconditions if p not in facts]
    if missing:
        raise AssertionError(f"preconditions failed: {missing}")


def assert_post(contract: CapabilityContract, facts: set[str]) -> None:
    missing = [p for p in contract.postconditions if p not in facts]
    if missing:
        raise AssertionError(f"postconditions failed: {missing}")
