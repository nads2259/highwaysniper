"""Ports for authoring agent packages on the repository filesystem."""

from typing import Protocol


class AgentPackageWriter(Protocol):
    def write_tree(self, agent_id: str, files: dict[str, str]) -> str:
        """Write agents/<agent_id>/ and return the path."""
