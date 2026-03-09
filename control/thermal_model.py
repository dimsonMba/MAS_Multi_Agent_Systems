"""Simple thermal dynamics helper."""


def next_temperature(current: float, ambient: float, fan_speed: int) -> float:
    """Estimate next temperature given ambient conditions and cooling."""
    cooling = fan_speed * 0.02
    drift = (ambient - current) * 0.1
    return current + drift - cooling
