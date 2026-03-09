"""Heartbeat protocol for liveness signaling."""


def send_heartbeat(agent) -> None:
    """Publish/update local liveness state.

    Future implementation:
    - broadcast to neighbors
    - update a shared heartbeat registry
    - include timestamp for timeout-based detection
    """
    # Scaffold no-op: heartbeat mechanics are intentionally left for algorithm work.
    _ = agent
