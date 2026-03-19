from mas.agents.base_agent import BaseMASAgent
from mas.protocols.kill_switch import should_trigger_kill_switch, get_kill_switch_reason
from mas.constants import EVENT_KILL_SWITCH_TRIGGERED


class SupervisorAgent(BaseMASAgent):
    """Global safety monitor and kill-switch controller."""

    def __init__(self, model, unique_id=None, *args, **kwargs):
        super().__init__(model, unique_id=unique_id, *args, **kwargs)
        self.safety_state = "normal"

    def step(self) -> None:
        triggered = should_trigger_kill_switch(self.model)

        if triggered:
            reason = get_kill_switch_reason(self.model)
            self.safety_state = "shutdown"

            if not self.model.system_shutdown:
                self.model.log_event(
                    EVENT_KILL_SWITCH_TRIGGERED,
                    reason=reason,
                    max_temp=self.model.get_max_temperature(),
                )

            self.model.system_shutdown = True
        else:
            self.safety_state = "normal"
