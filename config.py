"""Global configuration for simulation defaults.

Adjust these values to match experiment scenarios for resilience testing.
"""

DEFAULT_AGENT_COUNT = 12
DEFAULT_GRID_WIDTH = 20
DEFAULT_GRID_HEIGHT = 20
DEFAULT_STEPS = 50

# Failure injection settings
FAILURE_PROBABILITY = 0.03
HEARTBEAT_TIMEOUT_STEPS = 3

# Safety settings
CRITICAL_TEMPERATURE = 80.0
KILL_SWITCH_ENABLED = True
