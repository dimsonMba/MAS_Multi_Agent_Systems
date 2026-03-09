"""Safety kill-switch protocol."""

from config import KILL_SWITCH_ENABLED


def evaluate_kill_switch(model) -> None:
    """Stop simulation if safety hazard is active and switch is enabled."""
    if not KILL_SWITCH_ENABLED:
        return
    if model.environment.hazard_flag:
        model.running = False
