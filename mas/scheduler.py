"""Custom scheduler wrapper.

Mesa already provides several schedulers; this class leaves room for custom
activation order (for example: supervisor -> recovery -> thermal agents).
"""

from mesa.time import RandomActivation


class ResilienceScheduler(RandomActivation):
    """Simple extension point for deterministic or role-based stepping."""

    def step(self) -> None:
        # Keep default random activation for scaffold stage.
        super().step()
