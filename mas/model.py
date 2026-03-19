"""
Main Mesa model for the resilient thermal MAS.

Coordinates:
- local thermal regulation
- heartbeat-based failure detection
- consensus-driven reassignment
- resilience metrics and structured event logging
- global safety shutdown
"""

from __future__ import annotations

import random
from statistics import mean

from mesa import Model
from mesa.datacollection import DataCollector

from mas.agents.thermal_agent import ThermalAgent
from mas.agents.supervisor_agent import SupervisorAgent
from mas.protocols.heartbeat import detect_failed_agents
from mas.protocols.redistribution import redistribute_tasks
from mas.protocols.consensus import consensus_for_reassignment
from mas.environment import EnvironmentState
from mas.constants import (
    STATUS_FAILED,
    EVENT_AUTO_FAILURE_INJECTED,
    EVENT_RANDOM_FAILURE_INJECTED,
    EVENT_MANUAL_FAILURE_INJECTED,
    EVENT_HEARTBEAT_FAILURE_DETECTED,
    EVENT_UNSAFE_CONDITION_TRIGGERED,
)
from config import HEARTBEAT_TIMEOUT


class ThermalMASModel(Model):
    """
    Research-grade resilient MAS model for decentralized thermal control.

    Features:
    - one thermal agent per zone
    - structured heartbeat failure detection
    - explainable consensus-based reassignment
    - workload redistribution
    - supervisory kill-switch
    - event logging for charts, papers, and poster storytelling
    """

    def __init__(
        self,
        num_agents: int = 3,
        width: int = 5,
        height: int = 5,
        initial_temps: list[float] | None = None,
        failure_step: int = 20,
        unsafe_temp_threshold: float = 80.0,
        target_temp: float = 35.0,
        random_seed: int | None = None,
    ):
        super().__init__()

        if random_seed is not None:
            random.seed(random_seed)

        self.num_agents = num_agents
        self.width = width
        self.height = height
        self.current_step = 0

        # Experiment parameters
        self.failure_step = failure_step
        self.target_temp = target_temp
        self.unsafe_temp_threshold = unsafe_temp_threshold
        self.heartbeat_timeout = HEARTBEAT_TIMEOUT
        self.max_failed_agents_before_shutdown = 2

        # System state
        self.system_shutdown = False
        self.recovery_events = 0

        # Failure bookkeeping
        self.failed_agents_current: list = []
        self.failed_agents_new: list = []
        # Backwards-compatible alias expected by kill-switch logic.
        self.failed_agents: list = []

        # Logs
        self.redistribution_log: list[dict] = []
        self.event_log: list[dict] = []

        # Environment
        self.environment = EnvironmentState()

        if initial_temps is None:
            initial_temps = [30.0] * num_agents

        # Plant state
        self.heat_sources = {i: 5.0 + i for i in range(num_agents)}
        self.zone_temperatures = {i: float(initial_temps[i]) for i in range(num_agents)}
        self.fan_speeds = {i: 0 for i in range(num_agents)}

        # Agents
        self.thermal_agents = [
            ThermalAgent(self, zone_id=i, initial_temp=float(initial_temps[i]))
            for i in range(num_agents)
        ]
        self.supervisor = SupervisorAgent(self, unique_id=num_agents)

        # Data collector
        self.datacollector = DataCollector(
            model_reporters={
                "step": lambda m: m.current_step,
                "failed_agents": lambda m: len([a for a in m.thermal_agents if a.status == STATUS_FAILED]),
                "recovery_events": lambda m: m.recovery_events,
                "system_shutdown": lambda m: m.system_shutdown,
                "max_temp": lambda m: max(m.zone_temperatures.values()) if m.zone_temperatures else 0.0,
                "avg_temp": lambda m: mean(m.zone_temperatures.values()) if m.zone_temperatures else 0.0,
            }
        )

    # ----------------------------------------------------
    # Logging / metrics helpers
    # ----------------------------------------------------

    def log_event(self, event_type: str, **payload) -> None:
        """Append a structured event for timelines, charts, and analysis."""
        self.event_log.append(
            {
                "step": self.current_step,
                "type": event_type,
                **payload,
            }
        )

    def get_max_temperature(self) -> float:
        """Return hottest zone temperature."""
        return max(self.zone_temperatures.values()) if self.zone_temperatures else 0.0

    def get_average_temperature(self) -> float:
        """Return average zone temperature."""
        return mean(self.zone_temperatures.values()) if self.zone_temperatures else 0.0

    def get_operational_ratio(self) -> float:
        """Fraction of agents still active or recovering."""
        if not self.thermal_agents:
            return 0.0
        active_like = len([a for a in self.thermal_agents if a.status != STATUS_FAILED])
        return active_like / len(self.thermal_agents)

    # ----------------------------------------------------
    # Safety / local sync
    # ----------------------------------------------------

    def check_local_safety(self, agent) -> None:
        """
        Sync the agent's primary zone temperature into the plant state.
        """
        self.zone_temperatures[agent.zone_id] = agent.temperature

    # ----------------------------------------------------
    # Failure injection
    # ----------------------------------------------------

    def inject_failure(self) -> None:
        """
        Inject a scheduled failure at failure_step for experiment repeatability.
        """
        if self.current_step == self.failure_step and self.thermal_agents:
            victim = random.choice(self.thermal_agents)
            victim.fail(reason="scheduled_failure")
            self.log_event(
                EVENT_AUTO_FAILURE_INJECTED,
                agent_id=victim.zone_id,
                reason="scheduled_failure",
            )

    def inject_failure_random(self) -> None:
        """Fail a random active agent for interactive testing."""
        active = [a for a in self.thermal_agents if a.status != STATUS_FAILED]
        if not active:
            return

        victim = random.choice(active)
        victim.fail(reason="random_failure")
        self.log_event(
            EVENT_RANDOM_FAILURE_INJECTED,
            agent_id=victim.zone_id,
            reason="random_failure",
        )

    def inject_failure_manual(self, agent_index: int) -> None:
        """Manually fail a selected agent from the UI."""
        if 0 <= agent_index < len(self.thermal_agents):
            victim = self.thermal_agents[agent_index]
            victim.fail(reason="manual_failure")
            self.log_event(
                EVENT_MANUAL_FAILURE_INJECTED,
                agent_id=victim.zone_id,
                reason="manual_failure",
            )

    def trigger_unsafe_condition(self, zone_index: int = 0) -> None:
        """
        Manually push one zone above the unsafe threshold.
        Useful for supervisor / kill-switch testing.
        """
        if 0 <= zone_index < self.num_agents:
            unsafe_temp = self.unsafe_temp_threshold + 5.0
            self.zone_temperatures[zone_index] = unsafe_temp
            self.thermal_agents[zone_index].temperature = unsafe_temp
            self.environment.hazard_flag = True

            self.log_event(
                EVENT_UNSAFE_CONDITION_TRIGGERED,
                zone_id=zone_index,
                temperature=unsafe_temp,
            )

    # ----------------------------------------------------
    # Failure handling
    # ----------------------------------------------------

    def handle_failure(self) -> None:
        """
        Run failure detection, consensus, and redistribution.
        """
        detected = detect_failed_agents(self)
        self.failed_agents_new = detected
        self.failed_agents_current = [a for a in self.thermal_agents if a.status == STATUS_FAILED]
        # Keep `failed_agents` alias in sync with current failed set.
        self.failed_agents = self.failed_agents_current

        for failed_agent in detected:
            if getattr(failed_agent, "tasks_reassigned", False):
                continue

            self.log_event(
                EVENT_HEARTBEAT_FAILURE_DETECTED,
                agent_id=failed_agent.zone_id,
                reason=getattr(failed_agent, "failure_reason", "heartbeat_timeout"),
                zones=list(getattr(failed_agent, "assigned_heat_sources", [])),
                task_load=failed_agent.task_load,
            )

            winner, scored_candidates = consensus_for_reassignment(self, failed_agent)

            if winner is not None:
                redistribute_tasks(self, failed_agent, receiver=winner)

    # ----------------------------------------------------
    # Main simulation loop
    # ----------------------------------------------------

    def step(self) -> None:
        """
        One simulation step:
        1. inject scheduled failure (if configured)
        2. run all thermal agents
        3. detect failures + reassign workload
        4. run supervisor
        5. collect data
        """
        if self.system_shutdown:
            self.datacollector.collect(self)
            return

        self.inject_failure()

        for agent in self.thermal_agents:
            agent.step()

        self.handle_failure()
        self.supervisor.step()

        # Keep hazard flag aligned with global safety state
        self.environment.hazard_flag = self.system_shutdown or (
            self.get_max_temperature() >= self.unsafe_temp_threshold
        )

        self.current_step += 1
        self.datacollector.collect(self)
