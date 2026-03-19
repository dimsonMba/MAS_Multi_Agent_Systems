"""Deprecated recovery agent (kept for compatibility).

The current architecture performs failure handling and redistribution in
`ThermalMASModel.handle_failure()` using heartbeat detection + consensus,
so this agent is not used by the main simulation path.
"""

from mas.agents.base_agent import BaseMASAgent


class RecoveryAgent(BaseMASAgent):
    """Compatibility stub. Not used by current simulation."""

    def step(self) -> None:
        # Intentionally no-op: redistribution is handled by the model.
        return
