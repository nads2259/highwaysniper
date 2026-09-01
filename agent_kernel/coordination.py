"""Multi-agent coordination safety: depth, cycles, budgets, ping-pong, cancellation."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CoordinationGuard:
    max_delegation_depth: int = 4
    max_replans: int = 5
    max_reflections: int = 8
    max_fan_out: int = 8
    max_child_agents: int = 8
    _edges: set[tuple[str, str]] = field(default_factory=set)
    _children: dict[str, int] = field(default_factory=dict)

    def delegate(self, parent: str, child: str, depth: int) -> None:
        if depth > self.max_delegation_depth:
            raise RuntimeError("max delegation depth exceeded")
        if parent == child:
            raise RuntimeError("circular self-delegation")
        if (child, parent) in self._edges:
            raise RuntimeError("circular delegation")
        self._edges.add((parent, child))
        self._children[parent] = self._children.get(parent, 0) + 1
        if self._children[parent] > self.max_child_agents:
            raise RuntimeError("budget multiplication via child agents")

    def assert_replans(self, count: int) -> None:
        if count > self.max_replans:
            raise RuntimeError("livelock: max replan count")

    def assert_reflections(self, count: int) -> None:
        if count > self.max_reflections:
            raise RuntimeError("livelock: max reflection count")

    def assert_fan_out(self, n: int) -> None:
        if n > self.max_fan_out:
            raise RuntimeError("fan-out exceeds bound")
