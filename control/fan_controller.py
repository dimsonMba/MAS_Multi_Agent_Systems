"""
Fan speed computation for thermal control.

Implements a simple proportional controller with:
- configurable gain
- optional deadband
- optional minimum actuation threshold
"""

def compute_fan_speed(
    current_temp: float,
    target_temp: float,
    max_speed: int = 255,
    kp: float = 10.0,
    deadband: float = 0.5,
    min_speed: int = 0,
) -> int:
    """
    Compute fan speed from temperature error.

    Args:
        current_temp: Measured zone temperature.
        target_temp: Desired temperature setpoint.
        max_speed: Maximum PWM-like command.
        kp: Proportional gain.
        deadband: Ignore very small errors to reduce oscillation.
        min_speed: Minimum nonzero actuation once control engages.

    Returns:
        Fan speed in [0, max_speed].
    """
    error = current_temp - target_temp

    if error <= deadband:
        return 0

    raw_speed = int(kp * error)
    speed = min(max_speed, raw_speed)

    if speed > 0:
        speed = max(speed, min_speed)

    return speed


def pwm_to_percent(speed: int, max_speed: int = 255) -> float:
    """Convert PWM-like speed command to percentage."""
    return (speed / max_speed) * 100.0
