"""Fan control logic abstraction."""

from mas.utils.helpers import clamp


def compute_fan_speed(target_temp: float, current_temp: float) -> int:
    """Compute proportional fan speed from temperature error."""
    error = current_temp - target_temp
    speed = clamp(error * 5.0, 0.0, 100.0)
    return int(speed)
