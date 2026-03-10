"""
Main Mesa model for the resilient thermal MAS.

Coordinates thermal agents, failure injection, heartbeat-based detection,
task redistribution, and safety supervision. Collects metrics for experiments.
"""

from mesa import Model
from mesa.datacollection import DataCollector

from mas.agents.thermal_agent import ThermalAgent
from mas.agents.supervisor_agent import SupervisorAgent
from mas.protocols.heartbeat import detect_failed_agents
from mas.protocols.redistribution import redistribute_tasks
from mas.protocols.consensus import consensus_for_reassignment

from config import HEARTBEAT_TIMEOUT


class ThermalMASModel(Model):
    """
    Mesa model for decentralized failure recovery in a thermal MAS.

    Manages thermal agents (one per zone), a supervisor for safety,
    failure injection, and recovery protocols. DataCollector records
    step, failed_agents, recovery_events, system_shutdown, max_temp.
    """

    def __init__(
        self,
        num_agents: int = 3,
        width: int = 5,
        height: int = 5,
        initial_temps: list | None = None,
        failure_step: int = 20,
        unsafe_temp_threshold: float = 80.0,
        target_temp: float = 35.0,
    ):
        super().__init__()
        self.num_agents = num_agents
        self.width = width
        self.height = height
        self.current_step = 0
        self.failure_step = failure_step
        self.target_temp = target_temp
        self.unsafe_temp_threshold = unsafe_temp_threshold
        self.heartbeat_timeout = HEARTBEAT_TIMEOUT
        self.max_failed_agents_before_shutdown = 2
        self.system_shutdown = False
        self.recovery_events = 0
        self.failed_agents = []
        self.redistribution_log: list[dict] = []  # For UI: [{step, from_agent, to_agent}, ...]
        self.event_log: list[dict] = []  # For UI + research timeline

        if initial_temps is None:
            initial_temps = [30.0] * num_agents

        self.heat_sources = {i: 5 + i for i in range(num_agents)}
        self.zone_temperatures = {i: initial_temps[i] for i in range(num_agents)}
        # One fan per zone – agents can control multiple fans when they take over.
        self.fan_speeds = {i: 0 for i in range(num_agents)}
        self.thermal_agents = [
            ThermalAgent(self, zone_id=i, initial_temp=initial_temps[i])
            for i in range(num_agents)
        ]
        # Supervisor uses a distinct unique_id (num_agents) so it doesn't collide
        self.supervisor = SupervisorAgent(self, unique_id=num_agents)
        self.datacollector = DataCollector(
            model_reporters={
                "step": lambda m: m.current_step,
                "failed_agents": lambda m: len([a for a in m.thermal_agents if a.status == "failed"]),
                "recovery_events": lambda m: m.recovery_events,
                "system_shutdown": lambda m: m.system_shutdown,
                "max_temp": lambda m: max(m.zone_temperatures.values()),
            }
        )

    def log_event(self, event_type: str, **payload) -> None:
        """Append a structured event for research timelines and UI logs."""
        self.event_log.append(
            {
                "step": self.current_step,
                "type": event_type,
                **payload,
            }
        )

    def check_local_safety(self, agent) -> None:
        """
        Sync agent's temperature into model state for safety checks.
        Called by each ThermalAgent after updating its zone temperature.
        """
        self.zone_temperatures[agent.zone_id] = agent.temperature

    def inject_failure(self) -> None:
        """
        At failure_step: fail one agent (random for simulation variety).
        """
        if self.current_step == self.failure_step and self.thermal_agents:
            import random

            idx = random.randint(0, len(self.thermal_agents) - 1)
            self.thermal_agents[idx].fail()
            self.log_event("auto_failure_injected", agent=idx)

    def inject_failure_random(self) -> None:
        """Fail a random active agent (for UI 'Inject random failure')."""
        import random

        active = [a for a in self.thermal_agents if a.status == "active"]
        if not active:
            return
        victim = random.choice(active)
        victim.fail()
        self.log_event("random_failure_injected", agent=victim.zone_id)

    def inject_failure_manual(self, agent_index: int) -> None:
        """
        Manually fail an agent (for UI-triggered failure injection).
        """
        if 0 <= agent_index < len(self.thermal_agents):
            self.thermal_agents[agent_index].fail()
            self.log_event("manual_failure_injected", agent=agent_index)

    def trigger_unsafe_condition(self, zone_index: int = 0) -> None:
        """
        Manually trigger unsafe condition by setting a zone temp above threshold.
        Used for UI testing of kill-switch.
        """
        unsafe_temp = self.unsafe_temp_threshold + 5.0
        for i in range(self.num_agents):
            self.zone_temperatures[i] = unsafe_temp
            self.thermal_agents[i].temperature = unsafe_temp

    def handle_failure(self) -> None:
        """
        Run failure detection, consensus, and task redistribution.
        Detects failed agents via heartbeat timeout, picks a receiver
        via consensus, and redistributes the failed agent's tasks.
        """
        detected = detect_failed_agents(self)
        self.failed_agents = detected

        for failed_agent in detected:
            # Skip agents whose tasks are already fully reassigned.
            if getattr(failed_agent, "tasks_reassigned", False):
                continue

            # Heartbeat-based failure detection event
            self.log_event(
                "heartbeat_failure_detected",
                agent=failed_agent.zone_id,
            )

            winner = consensus_for_reassignment(self, failed_agent)
            if winner is not None:
                self.log_event(
                    "consensus_assignment",
                    from_agent=failed_agent.zone_id,
                    to_agent=winner.zone_id,
                )
                redistribute_tasks(self, failed_agent, receiver=winner)

    def step(self) -> None:
        """
        One simulation step: inject failures, run agents, handle recovery,
        run supervisor, advance step, collect metrics.
        """
        if self.system_shutdown:
            self.datacollector.collect(self)
            return

        self.inject_failure()

        for agent in self.thermal_agents:
            agent.step()

        self.handle_failure()
        self.supervisor.step()

        self.current_step += 1
        self.datacollector.collect(self)
