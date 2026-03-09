"""Base agent abstraction for shared resilience behavior."""

from mesa import Agent


class BaseResilientAgent(Agent):
    """Common state and helper behavior for MAS agents."""

    def __init__(self, unique_id: int, model) -> None:
        super().__init__(unique_id, model)
        self.failed = False
        self.assigned_tasks: list[str] = []

    def is_operational(self) -> bool:
        """Return True when the agent is available to process tasks."""
        return not self.failed
