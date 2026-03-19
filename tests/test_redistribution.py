"""Redistribution protocol correctness tests."""

from types import SimpleNamespace

from mas.protocols.redistribution import redistribute_tasks


class FakeAgent:
    def __init__(self, zone_id: int, status: str, assigned_heat_sources: list[int]):
        self.zone_id = zone_id
        self.status = status
        self.assigned_heat_sources = list(assigned_heat_sources)
        self.target_load = 1.0
        self.tasks_reassigned = False

    @property
    def task_load(self) -> int:
        return len(self.assigned_heat_sources)


def test_redistribution_transfers_all_zones_and_clears_failed_agent() -> None:
    model = SimpleNamespace(current_step=10, recovery_events=0, redistribution_log=[])
    receiver = FakeAgent(zone_id=0, status="active", assigned_heat_sources=[0])
    failed = FakeAgent(zone_id=1, status="failed", assigned_heat_sources=[1, 2])

    redistribute_tasks(model, failed_agent=failed, receiver=receiver)

    # Receiver keeps its original zone + inherited zones.
    assert set(receiver.assigned_heat_sources) == {0, 1, 2}
    # Failed agent no longer owns inherited responsibilities.
    assert failed.assigned_heat_sources == []
    assert failed.tasks_reassigned is True


def test_redistribution_is_idempotent_for_failed_agent() -> None:
    model = SimpleNamespace(current_step=10, recovery_events=0, redistribution_log=[])
    receiver = FakeAgent(zone_id=0, status="active", assigned_heat_sources=[0])
    failed = FakeAgent(zone_id=1, status="failed", assigned_heat_sources=[1])

    redistribute_tasks(model, failed_agent=failed, receiver=receiver)
    first = list(receiver.assigned_heat_sources)

    # Calling again should do nothing (idempotence).
    redistribute_tasks(model, failed_agent=failed, receiver=receiver)
    second = list(receiver.assigned_heat_sources)

    assert first == second
    assert set(receiver.assigned_heat_sources) == {0, 1}

