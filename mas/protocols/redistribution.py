"""
Task redistribution protocol: reassign a failed agent's workload.

Transfers the failed agent's assigned_heat_sources to the chosen
receiver and increments recovery_events for metrics.
"""


def redistribute_tasks(model, failed_agent, receiver=None) -> None:
    """
    Transfer the failed agent's heat sources to the consensus-chosen receiver.

    Args:
        model: ThermalMASModel.
        failed_agent: The agent that failed (source of tasks).
        receiver: The agent selected by the consensus protocol. If None, this
            function is a no-op to avoid re-running selection logic silently.
    """
    if receiver is None:
        return

    # Avoid duplicate reassignment if this failed agent was already processed.
    if getattr(failed_agent, "tasks_reassigned", False):
        return

    # Move ownership of all heat sources from failed_agent to receiver.
    sources = list(getattr(failed_agent, "assigned_heat_sources", []))
    for src in sources:
        if src not in receiver.assigned_heat_sources:
            receiver.assigned_heat_sources.append(src)

    # Clear tasks from the failed agent so UI/controller queries see the new owner only.
    failed_agent.assigned_heat_sources = []

    receiver.target_load += 1.0
    failed_agent.tasks_reassigned = True
    model.recovery_events += 1
    if hasattr(model, "redistribution_log"):
        model.redistribution_log.append({
            "step": model.current_step,
            "from_agent": failed_agent.zone_id,
            "to_agent": receiver.zone_id,
        })
