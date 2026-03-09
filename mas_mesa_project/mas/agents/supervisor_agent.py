"""Supervisor agent for safety oversight."""

from config import CRITICAL_TEMPERATURE
from mas.agents.base_agent import BaseResilientAgent
from mas.protocols.kill_switch import evaluate_kill_switch


class SupervisorAgent(BaseResilientAgent):
    """Monitors global safety state and can trigger kill-switch."""

    def step(self) -> None:
        if self.failed:
            return

        # Placeholder: use ambient temperature as the monitored variable.
        ambient = self.model.environment.ambient_temperature
        if ambient >= CRITICAL_TEMPERATURE:
            self.model.environment.hazard_flag = True

        evaluate_kill_switch(self.model)
