"""
Consensus protocol: pick which active agent should receive redistributed tasks.

Strategy:
  1. Prefer the agent closest to the failed agent (by zone index).
  2. If that agent's zone is hot (high temperature), prefer the agent with
     the lowest temperature so we don't overload an already-hot zone.
  So we sort by (distance_to_failed, temperature_ascending).
"""


def consensus_for_reassignment(model, failed_agent):
    """
    Select the best active agent to receive tasks from the failed agent.

    Picks the agent that is (1) closest to the failed agent, and (2) has
    the lowest temperature among candidates (so if the closest is already
    hot, we pick a cooler one to avoid overheating).

    Args:
        model: ThermalMASModel with thermal_agents.
        failed_agent: The agent that failed (source of tasks).

    Returns:
        The chosen ThermalAgent, or None if no candidates.
    """
    active_agents = [
        a for a in model.thermal_agents
        if a.status == "active" and a != failed_agent
    ]
    if not active_agents:
        return None

    failed_zone = failed_agent.zone_id

    # Sort by: (1) distance to failed zone (closest first), (2) temperature (coolest first)
    def key(a):
        distance = abs(a.zone_id - failed_zone)
        temp = a.temperature
        return (distance, temp)

    winner = min(active_agents, key=key)
    return winner
