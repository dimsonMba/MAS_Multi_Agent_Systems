"""
Task redistribution protocol: reassign a failed agent's workload.

Transfers the failed agent's assigned_heat_sources to the chosen
receiver and increments recovery_events for metrics.
"""


def redistribute_tasks(model, failed_agent) -> None:
    """
    Transfer the failed agent's heat sources to the least-loaded active agent.

    The receiver is chosen by consensus_for_reassignment. This function
    updates assigned_heat_sources and target_load, and increments
    model.recovery_events.

    Args:
        model: ThermalMASModel.
        failed_agent: The agent that failed (source of tasks).
    """
    candidates = [
        a for a in model.thermal_agents
        if a.status == "active" and a != failed_agent
    ]
    if not candidates:
        return

    candidates.sort(key=lambda a: a.task_load)
    receiver = candidates[0]

    receiver.assigned_heat_sources.extend(failed_agent.assigned_heat_sources)
    receiver.target_load += 1.0
    model.recovery_events += 1
    if hasattr(model, "redistribution_log"):
        model.redistribution_log.append({
            "step": model.current_step,
            "from_agent": failed_agent.zone_id,
            "to_agent": receiver.zone_id,
        })
