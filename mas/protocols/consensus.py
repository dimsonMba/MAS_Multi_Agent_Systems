"""
Consensus protocol: select the best active agent for workload reassignment.

Selection is based on a weighted score over:
- workload
- temperature
- thermal risk margin
- topological distance
"""

def candidate_score_breakdown(model, failed_agent, candidate) -> dict:
    workload = float(candidate.task_load)
    temp = float(candidate.temperature)
    unsafe = float(getattr(model, "unsafe_temp_threshold", 80.0))
    margin = max(0.0, unsafe - temp)
    distance = abs(candidate.zone_id - failed_agent.zone_id)

    norm_distance = float(distance)
    norm_workload = workload
    norm_temp = temp / max(unsafe, 1.0)
    norm_margin_risk = 1.0 - (margin / max(unsafe, 1.0))

    weights = {
        "distance": 1.0,
        "workload": 1.5,
        "temp": 2.0,
        "margin_risk": 2.5,
    }

    score = (
        weights["distance"] * norm_distance
        + weights["workload"] * norm_workload
        + weights["temp"] * norm_temp
        + weights["margin_risk"] * norm_margin_risk
    )

    return {
        "candidate_id": candidate.zone_id,
        "score": score,
        "distance": norm_distance,
        "workload": norm_workload,
        "temp": norm_temp,
        "margin_risk": norm_margin_risk,
        "weights": weights,
    }


def consensus_for_reassignment(model, failed_agent):
    """
    Select the best active agent to receive tasks from a failed agent.

    Returns:
        winner, score_breakdown_list
    """
    active_agents = [
        a for a in model.thermal_agents
        if a.status == "active" and a != failed_agent
    ]

    if not active_agents:
        return None, []

    scored = [
        candidate_score_breakdown(model, failed_agent, a)
        for a in active_agents
    ]
    scored.sort(key=lambda x: x["score"])

    winner_id = scored[0]["candidate_id"]
    winner = next(a for a in active_agents if a.zone_id == winner_id)

    if hasattr(model, "log_event"):
        model.log_event(
            "consensus_completed",
            failed_agent=failed_agent.zone_id,
            winner=winner.zone_id,
            winner_score=scored[0]["score"],
        )

    return winner, scored
