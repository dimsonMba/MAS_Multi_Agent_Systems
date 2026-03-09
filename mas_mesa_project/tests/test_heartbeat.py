"""Heartbeat protocol smoke test."""

from mas.protocols.heartbeat import send_heartbeat


def test_send_heartbeat_no_exception() -> None:
    class DummyAgent:
        pass

    send_heartbeat(DummyAgent())
