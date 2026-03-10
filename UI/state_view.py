"""
MAS state view: agent status, heartbeat, redistribution log, kill-switch.

Displays the right-side panel of the dashboard.
"""

import streamlit as st

from .components import agent_card, kill_switch_banner, redistribution_log_entries, ICONS


def render_mas_state(model, heartbeat_timeout: int = 3) -> None:
    """
    Render the MAS state panel:
    - Agent status (active/failed/recovering)
    - Heartbeat status
    - Task redistribution log
    - Kill-switch status
    """
    st.subheader(f"{ICONS['agent']} MAS State")

    for i, agent in enumerate(model.thermal_agents):
        agent_card(
            zone_id=i,
            status=agent.status,
            task_load=agent.task_load,
            last_seen=agent.last_seen_step,
            current_step=model.current_step,
            heartbeat_timeout=heartbeat_timeout,
        )

    st.divider()
    kill_switch_banner(model.system_shutdown)

    st.divider()
    st.caption(f"{ICONS['recovery']} **Redistribution Log**")
    log = getattr(model, "redistribution_log", [])
    redistribution_log_entries(log)
