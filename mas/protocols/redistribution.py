"""
Task redistribution protocol: reassign workload from failed agents to active agents.
"""

def redistribute_tasks(model, failed_agent, receiver=None) -> None:
    """
    Reassign all zones controlled by the failed agent to the receiver.
    """
    if receiver is None:
        return

    if getattr(failed_agent, "tasks_reassigned", False):
        return

    sources = list(getattr(failed_agent, "assigned_heat_sources", []))
    if not sources:
        return

    old_receiver_load = receiver.task_load
    old_failed_load = len(sources)

    moved_sources = []
    for src in sources:
        if src not in receiver.assigned_heat_sources:
            receiver.assigned_heat_sources.append(src)
            moved_sources.append(src)

    failed_agent.assigned_heat_sources = []
    failed_agent.tasks_reassigned = True
    receiver.target_load += len(moved_sources)
    model.recovery_events += 1

    event_payload = {
        "step": model.current_step,
        "from_agent": failed_agent.zone_id,
        "to_agent": receiver.zone_id,
        "zones": moved_sources,
        "failed_agent_reason": getattr(failed_agent, "failure_reason", None),
        "old_receiver_load": old_receiver_load,
        "new_receiver_load": receiver.task_load,
        "recovery_events": model.recovery_events,
    }

    if hasattr(model, "redistribution_log"):
        model.redistribution_log.append(event_payload)

    if hasattr(model, "log_event"):
        model.log_event("zone_reassigned", **event_payload)
