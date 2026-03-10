"""
Simulation controller: bridges UI and Mesa model.

Handles manual/auto stepping, failure injection, unsafe trigger,
reset, and history for charts. Keeps simulation layer separate from UI.
"""

from mas.model import ThermalMASModel


class SimulationController:
    """
    Wraps ThermalMASModel for UI control.
    Supports manual step, auto run, inject failure, trigger unsafe, reset.
    """

    def __init__(self, **model_kwargs):
        self.model_kwargs = model_kwargs
        self.model = ThermalMASModel(**model_kwargs)
        self.history: list[dict] = [self._snapshot()]  # Initial state for charts

    def _snapshot(self) -> dict:
        """Capture current state for charts."""
        temps = [self.model.zone_temperatures.get(i, 0.0) for i in range(self.model.num_agents)]
        # One fan per zone, independent of which agent controls it.
        fan_speeds = [self.model.fan_speeds.get(i, 0) for i in range(self.model.num_agents)]
        task_loads = [a.task_load for a in self.model.thermal_agents]
        agent_states = [a.status for a in self.model.thermal_agents]
        return {
            "step": self.model.current_step,
            "temps": temps.copy(),
            "fan_speeds": fan_speeds.copy(),
            "task_loads": task_loads.copy(),
            "agent_states": agent_states.copy(),
            "failed_agents": len([a for a in self.model.thermal_agents if a.status == "failed"]),
            "recovery_events": self.model.recovery_events,
            "system_shutdown": self.model.system_shutdown,
        }

    def run_step(self) -> None:
        """Advance simulation by one step."""
        self.model.step()
        self.history.append(self._snapshot())

    def inject_failure(self, agent_index: int = 1) -> None:
        """Manually fail a chosen agent."""
        self.model.inject_failure_manual(agent_index)
        self.history.append(self._snapshot())

    def inject_failure_random(self) -> None:
        """Fail a random active agent."""
        self.model.inject_failure_random()
        self.history.append(self._snapshot())

    def trigger_unsafe(self, zone_index: int = 0) -> None:
        """Manually trigger unsafe condition (kill-switch)."""
        self.model.trigger_unsafe_condition(zone_index)
        # Run one more step so supervisor sees it
        self.model.supervisor.step()
        self.history.append(self._snapshot())

    def set_zone_temp(self, zone_id: int, temp: float) -> None:
        """Manually set zone temperature (for UI override)."""
        if 0 <= zone_id < len(self.model.thermal_agents):
            self.model.thermal_agents[zone_id].temperature = temp
            self.model.zone_temperatures[zone_id] = temp

    def set_fan_speed(self, zone_id: int, speed: int) -> None:
        """Manually set fan speed (0-255) for a zone."""
        if 0 <= zone_id < len(self.model.fan_speeds):
            self.model.fan_speeds[zone_id] = max(0, min(255, speed))

    def set_heat_source(self, zone_id: int, value: float) -> None:
        """Manually set heat source strength for a zone."""
        if 0 <= zone_id < len(self.model.heat_sources):
            self.model.heat_sources[zone_id] = max(0, value)

    def reset(self, **overrides) -> None:
        """Reset simulation with optional config overrides."""
        kwargs = {**self.model_kwargs, **overrides}
        self.model = ThermalMASModel(**kwargs)
        self.history = [self._snapshot()]
        self.model_kwargs = kwargs
