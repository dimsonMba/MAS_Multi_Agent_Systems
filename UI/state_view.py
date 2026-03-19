"""
MAS state view for research and industrial presentation.

Displays:
- supervisor state
- per-agent operational/liveness state
- kill-switch status
- redistribution history
- structured event timeline
"""

import streamlit as st

from .components import (
    agent_card,
    kill_switch_banner,
    redistribution_log_entries,
    supervisor_card,
    ICONS,
)


def _render_event_line(ev: dict) -> None:
    """Render one structured event in readable research language."""
    etype = ev.get("type", "")
    step = ev.get("step", 0)

    if etype == "auto_failure_injected":
        st.write(f"Step {step}: 🔴 Scheduled failure injected for Agent {ev.get('agent_id', 0) + 1}")
    elif etype == "random_failure_injected":
        st.write(f"Step {step}: 🔴 Random failure injected for Agent {ev.get('agent_id', 0) + 1}")
    elif etype == "manual_failure_injected":
        st.write(f"Step {step}: 🔴 Manual failure injected for Agent {ev.get('agent_id', 0) + 1}")
    elif etype == "agent_suspected":
        st.write(
            f"Step {step}: 💤 Agent {ev.get('agent_id', 0) + 1} entered suspect state "
            f"(missed heartbeats: {ev.get('missed_heartbeats', 0)})"
        )
    elif etype == "agent_failed":
        st.write(
            f"Step {step}: 💔 Agent {ev.get('agent_id', 0) + 1} marked failed "
            f"({ev.get('reason', 'unknown')})"
        )
    elif etype == "heartbeat_failure_detected":
        st.write(
            f"Step {step}: 📡 Heartbeat failure confirmed for Agent {ev.get('agent_id', 0) + 1}"
        )
    elif etype == "consensus_completed":
        st.write(
            f"Step {step}: 🤝 Consensus selected Agent {ev.get('winner', 0) + 1} "
            f"to receive workload from Agent {ev.get('failed_agent', 0) + 1}"
        )
    elif etype == "zone_reassigned":
        zones = ev.get("zones", [])
        zone_text = ", ".join([f"Zone {z + 1}" for z in zones]) if zones else "N/A"
        st.write(
            f"Step {step}: 🔄 Workload reassigned from Agent {ev.get('from_agent', 0) + 1} "
            f"to Agent {ev.get('to_agent', 0) + 1} | Zones: {zone_text}"
        )
    elif etype == "unsafe_condition_triggered":
        st.write(
            f"Step {step}: ⚠️ Unsafe condition injected in Zone {ev.get('zone_id', 0) + 1} "
            f"at {ev.get('temperature', 0):.1f} °C"
        )
    elif etype == "kill_switch_triggered":
        st.write(
            f"Step {step}: 🛑 Kill-switch activated "
            f"({ev.get('reason', 'unknown')}) | Max temp: {ev.get('max_temp', 0):.1f} °C"
        )
    else:
        st.write(f"Step {step}: {etype}")


def render_mas_state(model, heartbeat_timeout: int = 3) -> None:
    """Render full MAS state panel."""
    st.subheader(f"{ICONS['agent']} MAS State")

    supervisor_card(model)

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
    st.caption("Workload Redistribution Log")
    redistribution_log_entries(getattr(model, "redistribution_log", []))

    st.divider()
    st.caption("Structured Event Timeline")
    events = getattr(model, "event_log", [])

    if not events:
        st.info("No events recorded yet.")
        return

    for ev in reversed(events[-12:]):
        _render_event_line(ev)
