"""
Fan speed computation for thermal control.

Maps temperature error (current - target) to a PWM-like fan speed (0–255).
Used by ThermalAgent to decide how much cooling to apply.
"""


def compute_fan_speed(
    current_temp: float,
    target_temp: float,
    max_speed: int = 255,
) -> int:
    """
    Compute fan speed from temperature error (proportional control).

    If current_temp <= target_temp, returns 0 (no cooling needed).
    Otherwise, speed increases with error, capped at max_speed.

    Args:
        current_temp: Current zone temperature.
        target_temp: Desired temperature setpoint.
        max_speed: Maximum PWM value (default 255).

    Returns:
        Fan speed in range [0, max_speed].
    """
    error = current_temp - target_temp

    if error <= 0:
        return 0

    # Stronger gain: even small temp overshoot → enough fan to overcome heat gain
    speed = int(min(max_speed, error * 18))
    return speed
