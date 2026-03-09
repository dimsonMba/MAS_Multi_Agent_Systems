"""Recovery agent for decentralized reallocation decisions."""

from mas.agents.base_agent import BaseResilientAgent
from mas.protocols.redistribution import redistribute_tasks


class RecoveryAgent(BaseResilientAgent):
    """Coordinates task redistribution after detected failures."""

    def step(self) -> None:
        if self.failed:
            return
        redistribute_tasks(self.model)
