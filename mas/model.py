"""Mesa model for decentralized failure recovery experiments."""

from __future__ import annotations

import random

from mesa import Model
from mesa.space import MultiGrid

from config import FAILURE_PROBABILITY
from mas.agents.thermal_agent import ThermalAgent
from mas.environment import EnvironmentState
from mas.metrics import MetricsSnapshot
from mas.scheduler import ResilienceScheduler


class ResilientMASModel(Model):
    """Main simulation model.

    The scaffold currently injects random failures and records simple metrics.
    """

    def __init__(self, width: int, height: int, n_agents: int) -> None:
        super().__init__()
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = ResilienceScheduler(self)
        self.environment = EnvironmentState()
        self.current_step = 0
        self.failure_events = 0
        self.metrics_history: list[MetricsSnapshot] = []

        for i in range(n_agents):
            agent = ThermalAgent(unique_id=i, model=self)
            self.schedule.add(agent)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

    def _inject_failures(self) -> None:
        """Randomly fail active agents for baseline resilience testing."""
        for agent in self.schedule.agents:
            if agent.failed:
                continue
            if random.random() < FAILURE_PROBABILITY:
                agent.failed = True
                self.failure_events += 1

    def _collect_metrics(self) -> None:
        alive_agents = sum(1 for a in self.schedule.agents if not a.failed)
        failed_agents = sum(1 for a in self.schedule.agents if a.failed)
        total_agents = alive_agents + failed_agents
        operational_ratio = (alive_agents / total_agents) if total_agents else 0.0
        self.metrics_history.append(
            MetricsSnapshot(
                step=self.current_step,
                alive_agents=alive_agents,
                failed_agents=failed_agents,
                hazard_flag=self.environment.hazard_flag,
                total_failure_events=self.failure_events,
                operational_ratio=operational_ratio,
            )
        )

    def step(self) -> None:
        """Advance simulation by one tick."""
        self.current_step += 1
        self._inject_failures()
        self.schedule.step()
        self._collect_metrics()
