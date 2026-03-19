"""Custom scheduler for deterministic resilience experiments."""

from mesa.time import BaseScheduler


class ResilienceScheduler(BaseScheduler):
    """
    Deterministic scheduler for MAS resilience experiments.

    Intended order:
    1. thermal agents
    2. failure detection / redistribution handled by model
    3. supervisor
    """

    def step(self) -> None:
        for agent in list(self._agents.values()):
            agent.step()
        self.steps += 1
        self.time += 1
