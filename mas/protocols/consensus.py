"""
Consensus protocol: pick which active agent should receive redistributed tasks.

Research-grade scoring strategy:
  - Lower score = better candidate.
  - Score is a weighted combination of:
      * workload (task_load)
      * current temperature
      * thermal margin to unsafe threshold
      * distance/topology (zone index distance)
  - This is easy to explain and tune in a research setting.
"""


def _candidate_score(model, failed_agent, candidate) -> float:
    """
    Compute a weighted score for how suitable `candidate` is to take over
    the failed agent's workload.

    The lower the score, the better the candidate.
    """
    # Basic features
    workload = candidate.task_load
    temp = candidate.temperature
    unsafe = getattr(model, "unsafe_temp_threshold", 80.0)
    margin = max(0.0, unsafe - temp)
    distance = abs(candidate.zone_id - failed_agent.zone_id)

    # Normalised values
    norm_distance = float(distance)
    norm_workload = float(workload)
    norm_temp = temp / max(unsafe, 1.0)
    norm_margin = 1.0 - (margin / max(unsafe, 1.0))  # higher when close to unsafe

    # Weights (can be tuned later or exposed via config)
    w_distance = 1.0
    w_workload = 1.5
    w_temp = 2.0
    w_margin = 2.5

    score = (
        w_distance * norm_distance
        + w_workload * norm_workload
        + w_temp * norm_temp
        + w_margin * norm_margin
    )
    return score


def consensus_for_reassignment(model, failed_agent):
    """
    Select the best active agent to receive tasks from the failed agent.

    Uses a weighted scoring rule over candidate features so the decision
    can be explained as:
        - Prefer agents with lower workload,
        - Prefer cooler agents with more thermal headroom,
        - Prefer agents that are topologically closer.

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

    winner = min(active_agents, key=lambda a: _candidate_score(model, failed_agent, a))
    return winner

