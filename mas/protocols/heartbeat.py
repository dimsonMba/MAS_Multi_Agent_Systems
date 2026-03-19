"""
Heartbeat protocol: detect failed agents via missed heartbeats.

Liveness escalation:
- healthy -> suspect when heartbeat delay is detected
- suspect -> failed when timeout threshold is exceeded
"""

def detect_failed_agents(model) -> list:
    """
    Detect failed agents using heartbeat timeout logic.

    Returns:
        List of agents newly classified as failed this step.
    """
    newly_failed = []

    for agent in model.thermal_agents:
        # Explicitly failed agents (injected by the experiment UI/model)
        # should be considered immediately "newly detected" for recovery.
        # `ThermalMASModel.handle_failure()` will prevent repeated
        # redistribution via `tasks_reassigned`.
        if agent.status == "failed":
            newly_failed.append(agent)
            agent.liveness_state = "failed"
            continue

        dt = model.current_step - agent.last_seen_step

        if dt <= 0:
            if agent.liveness_state != "healthy":
                agent.liveness_state = "healthy"
            agent.missed_heartbeats = 0
            continue

        agent.missed_heartbeats = dt

        if 0 < dt <= model.heartbeat_timeout:
            if agent.liveness_state != "suspect":
                agent.liveness_state = "suspect"
                if hasattr(model, "log_event"):
                    model.log_event(
                        "agent_suspected",
                        agent_id=agent.zone_id,
                        step=model.current_step,
                        missed_heartbeats=dt,
                    )

        elif dt > model.heartbeat_timeout:
            agent.status = "failed"
            agent.liveness_state = "failed"
            agent.failure_reason = "heartbeat_timeout"
            newly_failed.append(agent)

            if hasattr(model, "log_event"):
                model.log_event(
                    "agent_failed",
                    agent_id=agent.zone_id,
                    step=model.current_step,
                    reason="heartbeat_timeout",
                )

    return newly_failed
