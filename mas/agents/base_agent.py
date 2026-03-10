"""
Base agent class for all MAS agents.

Provides common behavior for resilience experiments: status tracking,
heartbeat signaling, and failure/recovery lifecycle. Subclasses (e.g.,
ThermalAgent, SupervisorAgent) extend this to add domain-specific logic.
"""

from mesa import Agent


class BaseMASAgent(Agent):
    """
    Base class for all agents in the resilient MAS.

    Mesa's Agent requires a unique_id for scheduling and identification.
    This base adds: status (active/failed/recovering), neighbor tracking,
    and last_seen_step for heartbeat-based failure detection.
    """

    def __init__(self, model, unique_id=None, *args, **kwargs):
        """
        Args:
            model: Reference to the parent ThermalMASModel (Mesa requires this first).
            unique_id: Optional unique identifier. Use zone_id for thermal agents,
                or a dedicated id for supervisors. If None, Mesa leaves it unset.
        """
        super().__init__(model, *args, **kwargs)
        if unique_id is not None:
            self.unique_id = unique_id
        self.status = "active"
        self.neighbors = []
        self.last_seen_step = 0

    def send_heartbeat(self) -> None:
        """
        Signal that this agent is alive this step.
        Updates last_seen_step so peers can detect missed heartbeats.
        """
        self.last_seen_step = self.model.current_step

    def fail(self) -> None:
        """Mark this agent as failed (e.g., after timeout or explicit injection)."""
        self.status = "failed"

    def recover(self) -> None:
        """Mark this agent as recovering (transitional state before active)."""
        self.status = "recovering"
