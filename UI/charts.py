"""
Charts for the MAS simulation dashboard.

Temperature over time, fan speed over time, failed agents, recovery events.
Uses Plotly for interactive, publication-quality graphs.
"""

import plotly.graph_objects as go  # type: ignore
from plotly.subplots import make_subplots
import streamlit as st


def temp_chart(
    history: list,
    num_zones: int = 3,
    unsafe_threshold: float | None = None,
    target_temp: float | None = None,
    events: list | None = None,
) -> None:
    """Line chart: temperature per zone over time with failure/kill-switch markers."""
    if not history:
        st.info("No data yet. Run the simulation.")
        return

    fig = go.Figure()
    steps = [h["step"] for h in history]
    for z in range(num_zones):
        temps = [h["temps"][z] if z < len(h["temps"]) else 0 for h in history]
        fig.add_trace(
            go.Scatter(
                x=steps,
                y=temps,
                name=f"Zone {z + 1}",
                mode="lines+markers",
            )
        )

    # Research overlays: target and unsafe thresholds
    if target_temp is not None:
        fig.add_hline(
            y=target_temp,
            line=dict(color="green", dash="dash"),
            annotation_text="Target",
            annotation_position="top left",
        )
    if unsafe_threshold is not None:
        fig.add_hline(
            y=unsafe_threshold,
            line=dict(color="red", dash="dot"),
            annotation_text="Unsafe",
            annotation_position="top right",
        )

    # Vertical markers for failures and kill-switch for resilience storytelling.
    if events:
        fail_types = {
            "auto_failure_injected",
            "random_failure_injected",
            "manual_failure_injected",
        }
        for ev in events:
            step = ev.get("step")
            etype = ev.get("type")
            if etype in fail_types:
                fig.add_vline(
                    x=step,
                    line=dict(color="orange", dash="dash"),
                )
            elif etype == "kill_switch_triggered":
                fig.add_vline(
                    x=step,
                    line=dict(color="red", dash="solid", width=2),
                )

    fig.update_layout(
        title="🌡️ Temperature vs Time",
        xaxis_title="Step",
        yaxis_title="Temperature (°C)",
        template="plotly_dark",
        height=280,
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True, key="temp_chart")


def fan_temp_chart(history: list, num_zones: int = 3) -> None:
    """Scatter chart: fan speed vs temperature per zone."""
    if not history:
        st.info("No data yet. Run the simulation.")
        return

    fig = go.Figure()
    for z in range(num_zones):
        temps = [h["temps"][z] if z < len(h["temps"]) else None for h in history]
        speeds = [h["fan_speeds"][z] if z < len(h["fan_speeds"]) else None for h in history]
        # Convert fan speed to percentage for readability.
        speeds_pct = [(s or 0) * 100.0 / 255.0 for s in speeds]
        fig.add_trace(
            go.Scatter(
                x=temps,
                y=speeds_pct,
                mode="markers",
                name=f"Zone {z + 1}",
            )
        )

    fig.update_layout(
        title="🌀 Fan Speed vs Temperature",
        xaxis_title="Temperature (°C)",
        yaxis_title="Fan Speed (%)",
        template="plotly_dark",
        height=280,
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True, key="fan_vs_temp_chart")

def fan_speed_chart(history: list, num_zones: int = 3) -> None:
    """Line chart: fan speed per zone over time."""
    if not history:
        st.info("No data yet. Run the simulation.")
        return

    fig = go.Figure()
    steps = [h["step"] for h in history]
    for z in range(num_zones):
        speeds = [h["fan_speeds"][z] if z < len(h["fan_speeds"]) else 0 for h in history]
        fig.add_trace(go.Scatter(x=steps, y=speeds, name=f"Fan {z + 1}", mode="lines+markers"))

    fig.update_layout(
        title="🌀 Fan Speed vs Time",
        xaxis_title="Step",
        yaxis_title="Fan Speed (0-255)",
        template="plotly_dark",
        height=280,
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True, key="fan_chart")


def resilience_chart(history: list, events: list | None = None) -> None:
    """Combined chart: failed agents and recovery events over time."""
    if not history:
        st.info("No data yet. Run the simulation.")
        return

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Failed Agents", "Recovery Events"),
        vertical_spacing=0.15,
        row_heights=[0.5, 0.5],
    )
    steps = [h["step"] for h in history]
    failed = [h["failed_agents"] for h in history]
    recovery = [h["recovery_events"] for h in history]

    fig.add_trace(go.Scatter(x=steps, y=failed, name="Failed", fill="tozeroy"), row=1, col=1)
    fig.add_trace(go.Scatter(x=steps, y=recovery, name="Recovery", fill="tozeroy"), row=2, col=1)

    # Mark kill-switch activation (and other key events) as vertical lines.
    if events:
        kill_steps = [e["step"] for e in events if e.get("type") == "kill_switch_triggered"]
        for s in kill_steps:
            fig.add_vline(
                x=s,
                line=dict(color="red", dash="dash"),
                row=1,
                col=1,
            )
            fig.add_vline(
                x=s,
                line=dict(color="red", dash="dash"),
                row=2,
                col=1,
            )

    fig.update_layout(
        title="🛡️ Resilience Metrics",
        template="plotly_dark",
        height=400,
        margin=dict(l=40, r=20, t=60, b=40),
        showlegend=False,
    )
    fig.update_xaxes(title_text="Step", row=2, col=1)
    st.plotly_chart(fig, use_container_width=True, key="resilience_chart")


def agent_status_timeline(history: list, num_agents: int = 3) -> None:
    """
    Heatmap-style timeline of agent status over time.

    Encodes states as:
        0 = failed (red)
        1 = active (green)
        2 = reassigned (active with task_load > 1, blue)
    """
    if not history or "agent_states" not in history[0]:
        st.info("No agent state history yet. Run the simulation.")
        return

    steps = [h["step"] for h in history]
    z = []
    for a in range(num_agents):
        row = []
        for h in history:
            states = h.get("agent_states", [])
            loads = h.get("task_loads", [])
            status = states[a] if a < len(states) else "unknown"
            load = loads[a] if a < len(loads) else 0
            if status == "failed":
                val = 0
            elif status == "active" and load > 1:
                val = 2
            elif status == "active":
                val = 1
            else:
                val = 0
            row.append(val)
        z.append(row)

    fig = go.Figure(
        data=go.Heatmap(
            x=steps,
            y=[f"Agent {i + 1}" for i in range(num_agents)],
            z=z,
            colorscale=[
                [0.0, "#ef4444"],   # failed
                [0.5, "#22c55e"],   # active
                [1.0, "#3b82f6"],   # reassigned
            ],
            colorbar=dict(
                ticks="outside",
                tickvals=[0, 1, 2],
                ticktext=["Failed", "Active", "Reassigned"],
            ),
        )
    )

    fig.update_layout(
        title="🤖 Agent Status Timeline",
        xaxis_title="Step",
        yaxis_title="Agent",
        template="plotly_dark",
        height=260,
        margin=dict(l=40, r=20, t=50, b=40),
    )
    st.plotly_chart(fig, use_container_width=True, key="agent_status_timeline")

def workload_chart(history: list, num_agents: int = 3) -> None:
    """Line chart: agent task load (number of zones) over time."""
    if not history or "task_loads" not in history[0]:
        st.info("No workload data yet. Run the simulation.")
        return

    fig = go.Figure()
    steps = [h["step"] for h in history]
    for a in range(num_agents):
        loads = [h["task_loads"][a] if a < len(h["task_loads"]) else 0 for h in history]
        fig.add_trace(go.Scatter(x=steps, y=loads, name=f"Agent {a + 1}", mode="lines+markers"))

    fig.update_layout(
        title="🧠 Agent Workload (zones) vs Time",
        xaxis_title="Step",
        yaxis_title="Zones controlled",
        template="plotly_dark",
        height=280,
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True, key="workload_chart")


def all_charts(
    history: list,
    num_zones: int = 3,
    unsafe_threshold: float | None = None,
    target_temp: float | None = None,
    events: list | None = None,
) -> None:
    """Render all charts in a grid."""
    c1, c2 = st.columns(2)
    with c1:
        temp_chart(
            history,
            num_zones,
            unsafe_threshold=unsafe_threshold,
            target_temp=target_temp,
            events=events,
        )
    with c2:
        fan_speed_chart(history, num_zones)

    # Second row: control law + agent state timeline
    c3, c4 = st.columns(2)
    with c3:
        fan_temp_chart(history, num_zones)
    with c4:
        agent_status_timeline(history, num_zones)

    # Bottom: workload and resilience metrics
    workload_chart(history, num_zones)
    resilience_chart(history, events=events)
