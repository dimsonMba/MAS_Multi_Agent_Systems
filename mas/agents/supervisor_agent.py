"""
Supervisor agent: global safety monitor and kill-switch.

Checks whether temperatures or failure counts exceed thresholds and
triggers system shutdown when needed. Runs once per step after agents.
"""

from mas.agents.base_agent import BaseMASAgent
from mas.protocols.kill_switch import should_trigger_kill_switch


class SupervisorAgent(BaseMASAgent):
    """
    Agent that monitors global safety and triggers the kill-switch.

    Does not manage a thermal zone; only evaluates safety conditions
    and sets model.system_shutdown when thresholds are exceeded.
    """

    def __init__(self, model, unique_id=None, *args, **kwargs):
        super().__init__(model, unique_id=unique_id, *args, **kwargs)

    def step(self) -> None:
        """
        Check safety conditions; if triggered, shut down the system.
        """
        if should_trigger_kill_switch(self.model):
            if not self.model.system_shutdown:
                # Log only on first activation so the timeline has a single, clear event.
                self.model.log_event("kill_switch_triggered")
            self.model.system_shutdown = True
