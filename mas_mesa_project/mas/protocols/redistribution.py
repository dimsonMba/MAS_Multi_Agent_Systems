"""Task redistribution protocol after failure detection."""


def redistribute_tasks(model) -> None:
    """Move pending work away from failed agents.

    Current scaffold:
    - identifies healthy agents as potential receivers
    - leaves allocation strategy as a TODO
    """
    healthy = [agent for agent in model.schedule.agents if not agent.failed]
    _ = healthy
