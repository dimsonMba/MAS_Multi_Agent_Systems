"""Thermal agent construction test."""

from mas.agents.thermal_agent import ThermalAgent


def test_thermal_agent_initial_state() -> None:
    class DummyModel:
        pass

    agent = ThermalAgent(unique_id=1, model=DummyModel())
    assert agent.failed is False
    assert agent.local_temperature == 25.0
