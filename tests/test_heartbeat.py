"""Heartbeat protocol tests.

Validates suspicion escalation -> confirmed failure using the current
heartbeat protocol in `mas.protocols.heartbeat`.
"""

from mas.protocols.heartbeat import detect_failed_agents


class FakeAgent:
    def __init__(self, zone_id: int, last_seen_step: int, status: str = "active"):
        self.zone_id = zone_id
        self.status = status
        self.last_seen_step = last_seen_step
        self.liveness_state = "healthy"
        self.missed_heartbeats = 0
        self.failure_reason = None


class FakeModel:
    def __init__(self, current_step: int, heartbeat_timeout: int, agents: list[FakeAgent]):
        self.current_step = current_step
        self.heartbeat_timeout = heartbeat_timeout
        self.thermal_agents = agents
        # The protocol calls model.log_event optionally; we don't need it for logic.


def test_heartbeat_enters_suspect_before_failure() -> None:
    heartbeat_timeout = 4
    # dt = 3 -> within timeout band -> liveness_state becomes suspect
    agent = FakeAgent(zone_id=1, last_seen_step=0)
    model = FakeModel(current_step=3, heartbeat_timeout=heartbeat_timeout, agents=[agent])

    newly_failed = detect_failed_agents(model)
    assert newly_failed == []
    assert agent.status == "active"
    assert agent.liveness_state == "suspect"


def test_heartbeat_escalates_to_failed_after_timeout() -> None:
    heartbeat_timeout = 4
    # dt = 6 -> exceeds timeout -> status becomes failed
    agent = FakeAgent(zone_id=2, last_seen_step=0)
    model = FakeModel(current_step=6, heartbeat_timeout=heartbeat_timeout, agents=[agent])

    newly_failed = detect_failed_agents(model)
    assert newly_failed == [agent]
    assert agent.status == "failed"
    assert agent.liveness_state == "failed"
    assert agent.failure_reason == "heartbeat_timeout"
