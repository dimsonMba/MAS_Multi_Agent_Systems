"""Thermal worker agent.

This agent represents a unit responsible for local temperature-related tasks.
"""

from mas.agents.base_agent import BaseResilientAgent
from mas.protocols.heartbeat import send_heartbeat


class ThermalAgent(BaseResilientAgent):
    """Basic worker agent with heartbeat behavior."""

    def __init__(self, unique_id: int, model) -> None:
        super().__init__(unique_id, model)
        self.local_temperature = 25.0

    def step(self) -> None:
        """Perform one simulation step.

        In scaffold form, this only emits a heartbeat if the agent is healthy.
        """
        if self.failed:
            return
        send_heartbeat(self)
