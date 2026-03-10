"""
Heartbeat protocol: detect failed agents via missed heartbeats.

Upgraded protocol with suspicion and escalation:
- Each agent tracks missed_heartbeats and liveness_state (healthy/suspect/failed).
- When heartbeats are late but within timeout, agents enter a suspect state.
- When the timeout is exceeded, agents transition to failed.
"""


def detect_failed_agents(model) -> list:
    """
    Find agents that are failed or have missed too many heartbeats.

    Uses model.heartbeat_timeout and a softer "suspect" band:
    - If 0 < dt <= timeout: mark agent as suspect.
    - If dt > timeout: mark agent as failed.

    Args:
        model: ThermalMASModel with thermal_agents and heartbeat_timeout.

    Returns:
        List of agents considered failed this step.
    """
    failed = []

    for agent in model.thermal_agents:
        if agent.status == "failed":
            failed.append(agent)
            continue

        dt = model.current_step - agent.last_seen_step

        if dt > 0:
            agent.missed_heartbeats = dt

        if 0 < dt <= model.heartbeat_timeout:
            agent.liveness_state = "suspect"
        elif dt > model.heartbeat_timeout:
            agent.status = "failed"
            agent.liveness_state = "failed"
            failed.append(agent)

    return failed
