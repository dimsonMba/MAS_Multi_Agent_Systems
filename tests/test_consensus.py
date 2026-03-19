"""Tests for the consensus-based task reassignment protocol."""

from types import SimpleNamespace

from mas.protocols.consensus import consensus_for_reassignment


class FakeAgent:
    def __init__(self, zone_id: int, temp: float, task_load: int, status: str = "active"):
        self.zone_id = zone_id
        self.temperature = temp
        self._task_load = task_load
        self.status = status

    @property
    def task_load(self) -> int:
        return self._task_load


def _make_model(agents, unsafe: float = 80.0):
    return SimpleNamespace(thermal_agents=agents, unsafe_temp_threshold=unsafe)


def test_consensus_prefers_cooler_and_less_loaded_agent() -> None:
    """If two agents are equally distant, pick the cooler and less-loaded one."""
    failed = FakeAgent(zone_id=1, temp=60.0, task_load=1)
    a1 = FakeAgent(zone_id=0, temp=70.0, task_load=2)  # hotter, more loaded
    a2 = FakeAgent(zone_id=2, temp=40.0, task_load=1)  # cooler, lighter
    model = _make_model([failed, a1, a2])

    winner, _ = consensus_for_reassignment(model, failed)
    assert winner is a2


def test_consensus_avoids_agent_near_unsafe_threshold() -> None:
    """Prefer an agent with more thermal headroom even if distance is slightly worse."""
    failed = FakeAgent(zone_id=1, temp=60.0, task_load=1)
    near_unsafe = FakeAgent(zone_id=0, temp=78.0, task_load=1)  # very close to unsafe
    safer = FakeAgent(zone_id=3, temp=50.0, task_load=1)  # cooler but farther
    model = _make_model([failed, near_unsafe, safer], unsafe=80.0)

    winner, _ = consensus_for_reassignment(model, failed)
    assert winner is safer


def test_consensus_returns_none_if_no_active_candidates() -> None:
    """If all other agents are failed, consensus returns None."""
    failed = FakeAgent(zone_id=1, temp=60.0, task_load=1)
    other = FakeAgent(zone_id=0, temp=40.0, task_load=1, status="failed")
    model = _make_model([failed, other])

    winner, scored = consensus_for_reassignment(model, failed)
    assert winner is None
    assert scored == []

