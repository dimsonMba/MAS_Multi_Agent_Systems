"""
Heartbeat protocol: detect failed agents via missed heartbeats.

Agents call send_heartbeat() each step; if last_seen_step is too old
relative to current_step, the agent is marked failed and added to the
detected list for redistribution.
"""


def detect_failed_agents(model) -> list:
    """
    Find agents that are failed or have missed too many heartbeats.

    Uses model.heartbeat_timeout: if (current_step - last_seen_step) > timeout,
    the agent is marked failed. Explicitly failed agents are also included.

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

        if model.current_step - agent.last_seen_step > model.heartbeat_timeout:
            agent.status = "failed"
            failed.append(agent)

    return failed
