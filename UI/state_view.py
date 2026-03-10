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
            liveness_state=getattr(agent, "liveness_state", "healthy"),
        )

    st.divider()
    kill_switch_banner(model.system_shutdown)

    st.divider()
    st.caption(f"{ICONS['recovery']} **Redistribution Log**")
    log = getattr(model, "redistribution_log", [])
    redistribution_log_entries(log)

    # Event timeline: consensus, failures, recovery, kill-switch
    st.divider()
    st.caption("🧠 **Event Timeline (Failures, Consensus, Recovery, Kill-Switch)**")
    events = getattr(model, "event_log", [])
    if not events:
        st.info("No events yet. Run the simulation or inject a failure.")
    else:
        # Show most recent events first
        for ev in reversed(events[-12:]):
            etype = ev.get("type", "")
            step = ev.get("step", 0)
            if etype == "auto_failure_injected":
                st.write(f"Step {step}: 🔴 Auto failure injected for Agent {ev.get('agent', 0) + 1}")
            elif etype == "random_failure_injected":
                st.write(f"Step {step}: 🔴 Random failure injected for Agent {ev.get('agent', 0) + 1}")
            elif etype == "manual_failure_injected":
                st.write(f"Step {step}: 🔴 Manual failure injected for Agent {ev.get('agent', 0) + 1}")
            elif etype == "heartbeat_failure_detected":
                st.write(f"Step {step}: 💔 Heartbeat timeout — Agent {ev.get('agent', 0) + 1} considered failed")
            elif etype == "consensus_assignment":
                st.write(
                    f"Step {step}: 🤝 Consensus — Agent {ev.get('to_agent', 0) + 1} "
                    f"takes over tasks from Agent {ev.get('from_agent', 0) + 1}"
                )
            elif etype == "kill_switch_triggered":
                st.write(f"Step {step}: 🛑 Kill-switch activated — system shutdown")
            else:
                st.write(f"Step {step}: {etype}")
