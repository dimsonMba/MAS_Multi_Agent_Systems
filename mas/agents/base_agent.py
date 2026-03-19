"""
Base agent class for all MAS agents.

Provides shared resilience behavior:
- heartbeat signaling
- liveness monitoring
- failure / recovery lifecycle
- experiment tracking

Subclasses (ThermalAgent, SupervisorAgent, etc.) extend this class
to implement domain-specific control logic.
"""

from mesa import Agent


class BaseMASAgent(Agent):
    """
    Base class for resilient MAS agents.

    Adds distributed-system concepts on top of Mesa Agent:
    - heartbeat monitoring
    - failure detection
    - recovery lifecycle
    - neighbor awareness
    """

    def __init__(self, model, unique_id=None, *args, **kwargs):
        super().__init__(model, *args, **kwargs)

        if unique_id is not None:
            self.unique_id = unique_id

        # Operational state
        self.status = "active"       # active | recovering | failed

        # Network liveness state
        self.liveness_state = "healthy"  # healthy | suspect | failed

        # MAS network structure
        self.neighbors = []

        # Heartbeat tracking
        self.last_seen_step = 0
        self.missed_heartbeats = 0

        # Research metrics
        self.failure_reason = None

    # ----------------------------------------------------
    # Heartbeat
    # ----------------------------------------------------

    def send_heartbeat(self) -> None:
        """
        Broadcast a heartbeat to indicate the agent is alive.

        This resets missed heartbeat counters and restores
        the liveness state to healthy.
        """
        self.last_seen_step = self.model.current_step
        self.missed_heartbeats = 0

        if self.liveness_state in ("suspect", "failed"):
            self.liveness_state = "healthy"

    # ----------------------------------------------------
    # Liveness monitoring
    # ----------------------------------------------------

    def check_liveness(self, timeout: int = 3) -> None:
        """
        Detect missed heartbeats and transition states.

        Args:
            timeout: number of steps before declaring failure
        """

        steps_since_seen = self.model.current_step - self.last_seen_step

        if steps_since_seen > timeout:
            self.missed_heartbeats += 1

            if self.missed_heartbeats == 1:
                self.liveness_state = "suspect"

            elif self.missed_heartbeats >= 2:
                self.fail(reason="heartbeat_timeout")

    # ----------------------------------------------------
    # Failure lifecycle
    # ----------------------------------------------------

    def fail(self, reason: str = "unknown") -> None:
        """
        Mark this agent as failed.

        Args:
            reason: explanation for experiment tracking
        """
        self.status = "failed"
        self.liveness_state = "failed"
        self.failure_reason = reason

    def recover(self) -> None:
        """
        Move agent into recovering state.

        Supervisors or consensus algorithms may reassign
        tasks during this phase.
        """
        self.status = "recovering"
        self.liveness_state = "healthy"

    def activate(self) -> None:
        """
        Fully restore agent operation after recovery.
        """
        self.status = "active"
        self.failure_reason = None
