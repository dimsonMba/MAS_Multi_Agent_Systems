"""Thermal agent construction test."""

from types import SimpleNamespace

from mas.agents.thermal_agent import ThermalAgent


def test_thermal_agent_initial_state() -> None:
    dummy_model = SimpleNamespace(current_step=0)
    agent = ThermalAgent(dummy_model, zone_id=1, initial_temp=25.0)

    assert agent.status == "active"
    assert agent.liveness_state == "healthy"
    assert agent.zone_id == 1
    assert agent.temperature == 25.0
    assert agent.fan_speed == 0
    assert agent.assigned_heat_sources == [1]
