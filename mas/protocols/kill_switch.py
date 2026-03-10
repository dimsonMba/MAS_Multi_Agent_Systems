"""
Kill-switch protocol: decides when to shut down the system for safety.

Triggers when temperatures exceed threshold or too many agents have failed.
Used by SupervisorAgent each step.
"""


def should_trigger_kill_switch(model) -> bool:
    """
    Determine if the system should be shut down for safety.

    Conditions:
    - Already shut down (idempotent)
    - Any zone temperature >= unsafe_temp_threshold
    - Number of failed agents >= max_failed_agents_before_shutdown

    Args:
        model: ThermalMASModel with zone_temperatures, failed_agents, etc.

    Returns:
        True if kill-switch should trigger, False otherwise.
    """
    if model.system_shutdown:
        return True

    overheated = any(
        temp >= model.unsafe_temp_threshold
        for temp in model.zone_temperatures.values()
    )
    too_many_failures = (
        len(model.failed_agents) >= model.max_failed_agents_before_shutdown
    )

    return overheated or too_many_failures
