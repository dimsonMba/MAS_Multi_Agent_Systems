"""
Thermal dynamics for simulation.

Heat source adds heat; fan removes heat. When the fan runs at sufficient speed,
cooling overcomes heat gain and temperature drops or stabilizes.
"""

# Cooling strength: at full fan (255), cooling = COOLING_FACTOR.
# With a slightly lower factor, temperatures change more gradually so
# the research plots show visible dynamics instead of a perfectly flat line.
COOLING_FACTOR = 4.0


def update_temperature(
    current_temp: float,
    heat_input: float,
    fan_speed: float,
) -> float:
    """
    Compute next temperature: heat gain minus fan cooling.

    When fan runs at sufficient speed, cooling overcomes heat gain
    and temperature decreases. When fan is off or low, temperature rises.

    Args:
        current_temp: Current zone temperature.
        heat_input: Heat source strength (e.g., from model.heat_sources).
        fan_speed: Fan PWM value (0–255). Higher = more cooling.

    Returns:
        Next temperature (clamped to [0, 200]).
    """
    heat_gain = 0.15 * heat_input
    cooling = COOLING_FACTOR * (fan_speed / 255)
    next_temp = current_temp + heat_gain - cooling

    return max(0.0, min(200.0, next_temp))
