"""
Thermal dynamics for simulation.

The model approximates temperature evolution using:
- heat input from the environment / source
- cooling from fan actuation
- passive drift toward ambient temperature
- optional disturbance term for experiments
"""

AMBIENT_TEMP = 25.0
COOLING_FACTOR = 4.0
HEAT_GAIN_FACTOR = 0.15
AMBIENT_COUPLING = 0.03


def update_temperature(
    current_temp: float,
    heat_input: float,
    fan_speed: float,
    ambient_temp: float = AMBIENT_TEMP,
    disturbance: float = 0.0,
) -> float:
    """
    Compute the next zone temperature.

    Args:
        current_temp: Current temperature.
        heat_input: Heat source strength.
        fan_speed: Fan command (0-255).
        ambient_temp: Background environmental temperature.
        disturbance: Extra disturbance term for experiments.

    Returns:
        Next temperature, clamped to [0, 200].
    """
    heat_gain = HEAT_GAIN_FACTOR * heat_input
    cooling = COOLING_FACTOR * (fan_speed / 255.0)
    ambient_pull = AMBIENT_COUPLING * (ambient_temp - current_temp)

    next_temp = current_temp + heat_gain - cooling + ambient_pull + disturbance
    return max(0.0, min(200.0, next_temp))
