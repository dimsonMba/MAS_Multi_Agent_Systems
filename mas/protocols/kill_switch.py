"""
Kill-switch protocol: decide when emergency shutdown is required.
"""

def get_kill_switch_reason(model) -> str | None:
    """
    Return the reason for kill-switch activation, or None if safe.
    """
    overheated = any(
        temp >= model.unsafe_temp_threshold
        for temp in model.zone_temperatures.values()
    )

    too_many_failures = (
        len(model.failed_agents) >= model.max_failed_agents_before_shutdown
    )

    if overheated and too_many_failures:
        return "overheat_and_failure_limit"
    if overheated:
        return "overheat"
    if too_many_failures:
        return "failure_limit"
    return None


def should_trigger_kill_switch(model) -> bool:
    """
    Return True when emergency shutdown is required.
    """
    if model.system_shutdown:
        return True

    return get_kill_switch_reason(model) is not None
