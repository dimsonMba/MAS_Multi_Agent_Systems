"""
Thermal agent: monitors a zone's temperature and controls fan speed.

Each ThermalAgent is responsible for one zone. It reads temperature from
the thermal model, computes fan speed via the fan controller, and
participates in heartbeat-based failure detection and task redistribution.
"""

from mas.agents.base_agent import BaseMASAgent
from control.thermal_model import update_temperature
from control.fan_controller import compute_fan_speed


class ThermalAgent(BaseMASAgent):
    """
    Agent that monitors a thermal zone and adjusts fan speed.

    Attributes:
        zone_id: Index of the zone this agent manages.
        temperature: Current zone temperature (updated each step).
        fan_speed: Current fan output (0–255).
        target_load: Target workload factor (used for redistribution).
        assigned_heat_sources: List of zone IDs this agent is responsible for.
    """

    def __init__(self, model, zone_id: int, initial_temp: float = 25.0):
        super().__init__(model, unique_id=zone_id)
        self.zone_id = zone_id
        self.temperature = initial_temp
        self.fan_speed = 0
        self.target_load = 1.0
        self.assigned_heat_sources = [zone_id]

    @property
    def task_load(self) -> float:
        """
        Current workload (number of heat sources assigned).
        Used by consensus and redistribution to pick least-loaded agents.
        """
        return len(self.assigned_heat_sources)

    def monitor_temperature(self) -> None:
        """
        Update temperature for all zones this agent controls.
        When fan runs, cooling overcomes heat gain.
        """
        for z in self.assigned_heat_sources:
            curr = self.model.zone_temperatures.get(z, self.temperature)
            heat = self.model.heat_sources.get(z, 5)
            new_temp = update_temperature(
                current_temp=curr,
                heat_input=heat,
                fan_speed=self.fan_speed,
            )
            self.model.zone_temperatures[z] = new_temp
            if z == self.zone_id:
                self.temperature = new_temp

    def control_fan(self) -> None:
        """
        Compute fan speed from the hottest zone we control.
        Higher temp → higher fan speed → more cooling.
        """
        max_temp = max(
            self.model.zone_temperatures.get(z, self.temperature)
            for z in self.assigned_heat_sources
        )
        self.fan_speed = compute_fan_speed(
            current_temp=max_temp,
            target_temp=self.model.target_temp,
        )

    def step(self) -> None:
        """
        Mesa step: run each simulation tick.
        Skips if agent is failed or system is shut down.
        """
        if self.status == "failed" or self.model.system_shutdown:
            return

        self.send_heartbeat()
        self.monitor_temperature()
        self.control_fan()
        self.model.check_local_safety(self)
