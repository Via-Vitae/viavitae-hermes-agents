"""Minimal agent registry scaffold."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


class Agent(Protocol):
    """A named Via Vitae agent component."""

    name: str


@dataclass
class AgentRegistry:
    """A name-indexed collection of agents."""

    _agents: dict[str, Agent] = field(default_factory=dict)

    def register(self, agent: Agent) -> None:
        self._agents[agent.name] = agent

    def names(self) -> list[str]:
        return sorted(self._agents)
