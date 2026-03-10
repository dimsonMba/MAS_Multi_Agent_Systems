"""
Charts for the MAS simulation dashboard.

Temperature over time, fan speed over time, failed agents, recovery events.
Uses Plotly for interactive, publication-quality graphs.
"""

import plotly.graph_objects as go  # type: ignore
from plotly.subplots import make_subplots
import streamlit as st


def temp_chart(history: list, num_zones: int = 3) -> None:
    """Line chart: temperature per zone over time."""
    if not history:
        st.info("No data yet. Run the simulation.")
        return

    fig = go.Figure()
    steps = [h["step"] for h in history]
    for z in range(num_zones):
        temps = [h["temps"][z] if z < len(h["temps"]) else 0 for h in history]
        fig.add_trace(go.Scatter(x=steps, y=temps, name=f"Zone {z + 1}", mode="lines+markers"))

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


def resilience_chart(history: list) -> None:
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

    fig.update_layout(
        title="🛡️ Resilience Metrics",
        template="plotly_dark",
        height=400,
        margin=dict(l=40, r=20, t=60, b=40),
        showlegend=False,
    )
    fig.update_xaxes(title_text="Step", row=2, col=1)
    st.plotly_chart(fig, use_container_width=True, key="resilience_chart")


def all_charts(history: list, num_zones: int = 3) -> None:
    """Render all charts in a grid."""
    c1, c2 = st.columns(2)
    with c1:
        temp_chart(history, num_zones)
    with c2:
        fan_speed_chart(history, num_zones)
    resilience_chart(history)
