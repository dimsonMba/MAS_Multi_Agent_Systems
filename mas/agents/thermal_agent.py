"""
Thermal agent: monitors one or more thermal zones and controls fan speed.

Each ThermalAgent is responsible for local thermal regulation and can
temporarily assume responsibility for additional zones when failures occur.
This supports resilience experiments involving redistribution, overload,
and safe recovery.
"""

from mas.agents.base_agent import BaseMASAgent
from control.thermal_model import update_temperature
from control.fan_controller import compute_fan_speed


class ThermalAgent(BaseMASAgent):
    """
    Local thermal control agent for one or more zones.

    Attributes:
        zone_id: Primary zone originally assigned to this agent.
        temperature: Current temperature of the primary zone.
        fan_speed: Current fan command for the primary zone.
        assigned_heat_sources: Zones currently controlled by this agent.
        local_safety_state: safe | warning | unsafe
    """

    def __init__(self, model, zone_id: int, initial_temp: float = 25.0):
        super().__init__(model, unique_id=zone_id)
        self.zone_id = zone_id
        self.temperature = initial_temp
        self.fan_speed = 0
        self.target_load = 1.0
        self.assigned_heat_sources = [zone_id]
        self.local_safety_state = "safe"

    @property
    def task_load(self) -> int:
        """Number of zones currently managed by this agent."""
        return len(self.assigned_heat_sources)

    @property
    def is_overloaded(self) -> bool:
        """Indicates whether the agent is operating above nominal load."""
        return self.task_load > 1

    def monitor_temperature(self) -> None:
        """
        Update temperature dynamics for every assigned zone.
        """
        for z in self.assigned_heat_sources:
            curr = self.model.zone_temperatures.get(z, self.temperature)
            heat = self.model.heat_sources.get(z, 5)
            fan = self.model.fan_speeds.get(z, 0)

            new_temp = update_temperature(
                current_temp=curr,
                heat_input=heat,
                fan_speed=fan,
            )

            self.model.zone_temperatures[z] = new_temp

            if z == self.zone_id:
                self.temperature = new_temp

    def control_fan(self) -> None:
        """
        Compute fan command for each assigned zone.

        Under redistributed workload, the same agent can command multiple
        physical fans across multiple zones.
        """
        for z in self.assigned_heat_sources:
            temp_z = self.model.zone_temperatures.get(z, self.temperature)

            fan = compute_fan_speed(
                current_temp=temp_z,
                target_temp=self.model.target_temp,
            )

            self.model.fan_speeds[z] = fan

        self.fan_speed = self.model.fan_speeds.get(self.zone_id, 0)

    def evaluate_local_safety(self) -> None:
        """
        Track local safety condition of the primary zone for logging and charts.
        """
        unsafe = getattr(self.model, "unsafe_temp_threshold", None)

        if unsafe is None:
            self.local_safety_state = "safe"
            return

        if self.temperature >= unsafe:
            self.local_safety_state = "unsafe"
        elif self.temperature >= unsafe - 3:
            self.local_safety_state = "warning"
        else:
            self.local_safety_state = "safe"

    def step(self) -> None:
        """
        Execute one local control cycle.
        """
        if self.status == "failed" or self.model.system_shutdown:
            return

        self.send_heartbeat()
        self.monitor_temperature()
        self.control_fan()
        self.evaluate_local_safety()
        self.model.check_local_safety(self)
