"""
Research-grade charts for the MAS dashboard.

Visualizes:
- temperature stability
- fan response
- agent state timeline
- workload redistribution
- resilience metrics
"""

import plotly.graph_objects as go  # type: ignore
from plotly.subplots import make_subplots
import streamlit as st

CHART_HEIGHT_SMALL = 320
CHART_HEIGHT_MEDIUM = 380
CHART_HEIGHT_LARGE = 430
FONT_FAMILY = "Arial, sans-serif"


def _base_layout(fig: go.Figure, title: str, height: int) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, x=0.02, xanchor="left"),
        template="plotly_dark",
        height=height,
        margin=dict(l=50, r=25, t=60, b=45),
        font=dict(family=FONT_FAMILY, size=13),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
        ),
        hovermode="x unified",
    )
    return fig


def _add_event_lines(
    fig: go.Figure,
    events: list | None,
    row: int | None = None,
    col: int | None = None,
) -> None:
    """Overlay event markers on charts.

    Important: avoid repeated annotation text (it becomes unreadable).
    We annotate only the first occurrence of each label.
    """
    if not events:
        return

    labeled: set[str] = set()

    for ev in events:
        step = ev.get("step")
        etype = ev.get("type", "")

        color = None
        dash = "dash"
        label = None

        if etype in {"auto_failure_injected", "random_failure_injected", "manual_failure_injected"}:
            color = "orange"
            label = "Failure Injected"
        elif etype in {"agent_failed", "heartbeat_failure_detected"}:
            color = "gold"
            label = "Failure Detected"
        elif etype in {"consensus_completed", "zone_reassigned"}:
            color = "deepskyblue"
            label = "Recovery / Reassignment"
        elif etype == "kill_switch_triggered":
            color = "red"
            dash = "solid"
            label = "Kill Switch"

        if color is None:
            continue

        # Only annotate the first occurrence per label to avoid overlapping text.
        annotation_text = None
        if label and label not in labeled:
            annotation_text = label
            labeled.add(label)

        kwargs = dict(
            x=step,
            line=dict(color=color, dash=dash, width=2),
            annotation_text=annotation_text,
            annotation_position="top left",
            opacity=0.8,
        )

        if row is not None and col is not None:
            fig.add_vline(row=row, col=col, **kwargs)
        else:
            fig.add_vline(**kwargs)


def temp_chart(
    history: list,
    num_zones: int = 3,
    unsafe_threshold: float | None = None,
    target_temp: float | None = None,
    events: list | None = None,
) -> None:
    if not history:
        st.info("No data yet.")
        return

    steps = [h["step"] for h in history]
    fig = go.Figure()

    for z in range(num_zones):
        temps = [h["temps"][z] if z < len(h["temps"]) else None for h in history]
        fig.add_trace(
            go.Scatter(
                x=steps,
                y=temps,
                mode="lines",
                name=f"Zone {z + 1}",
                line=dict(width=3),
            )
        )

    if target_temp is not None:
        fig.add_hline(
            y=target_temp,
            line=dict(color="limegreen", dash="dash", width=2),
            annotation_text="Target Temperature",
            annotation_position="top left",
        )

    if unsafe_threshold is not None:
        fig.add_hline(
            y=unsafe_threshold,
            line=dict(color="red", dash="dot", width=2),
            annotation_text="Unsafe Threshold",
            annotation_position="top right",
        )
        fig.add_hrect(
            y0=unsafe_threshold,
            y1=max(max(h["temps"]) for h in history) + 5,
            fillcolor="rgba(255, 0, 0, 0.12)",
            line_width=0,
            annotation_text="Unsafe Region",
            annotation_position="top left",
        )

    _add_event_lines(fig, events)

    fig.update_xaxes(title_text="Simulation Step")
    fig.update_yaxes(title_text="Temperature (°C)")
    _base_layout(fig, "Zone Temperature Stability Over Time", CHART_HEIGHT_MEDIUM)
    st.plotly_chart(fig, use_container_width=True, key="temp_chart")


def fan_speed_chart(history: list, num_zones: int = 3) -> None:
    if not history:
        st.info("No data yet.")
        return

    steps = [h["step"] for h in history]
    fig = go.Figure()

    for z in range(num_zones):
        speeds = [h["fan_speeds"][z] if z < len(h["fan_speeds"]) else 0 for h in history]
        speeds_pct = [(s * 100.0) / 255.0 for s in speeds]
        fig.add_trace(
            go.Scatter(
                x=steps,
                y=speeds_pct,
                mode="lines",
                name=f"Fan {z + 1}",
                line=dict(width=3),
            )
        )

    fig.update_xaxes(title_text="Simulation Step")
    fig.update_yaxes(title_text="Fan Speed (%)", range=[0, 100])
    _base_layout(fig, "Fan Control Response Over Time", CHART_HEIGHT_MEDIUM)
    st.plotly_chart(fig, use_container_width=True, key="fan_chart")


def fan_temp_chart(history: list, num_zones: int = 3, target_temp: float | None = None) -> None:
    if not history:
        st.info("No data yet.")
        return

    fig = go.Figure()

    for z in range(num_zones):
        temps = [h["temps"][z] if z < len(h["temps"]) else None for h in history]
        speeds = [h["fan_speeds"][z] if z < len(h["fan_speeds"]) else None for h in history]
        speeds_pct = [(s or 0) * 100.0 / 255.0 for s in speeds]

        fig.add_trace(
            go.Scatter(
                x=temps,
                y=speeds_pct,
                mode="markers+lines",
                name=f"Zone {z + 1}",
                marker=dict(size=7),
            )
        )

    if target_temp is not None:
        fig.add_vline(
            x=target_temp,
            line=dict(color="limegreen", dash="dash", width=2),
            annotation_text="Target Temp",
            annotation_position="top",
        )

    fig.update_xaxes(title_text="Temperature (°C)")
    fig.update_yaxes(title_text="Fan Speed (%)", range=[0, 100])
    _base_layout(fig, "Control Law Behavior: Fan Speed vs Temperature", CHART_HEIGHT_MEDIUM)
    st.plotly_chart(fig, use_container_width=True, key="fan_vs_temp_chart")


def resilience_chart(history: list, events: list | None = None) -> None:
    if not history:
        st.info("No data yet.")
        return

    steps = [h["step"] for h in history]
    failed = [h["failed_agents"] for h in history]
    recovery = [h["recovery_events"] for h in history]

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        subplot_titles=("Failed Agents Over Time", "Recovery Events Over Time"),
        vertical_spacing=0.14,
        row_heights=[0.5, 0.5],
    )

    fig.add_trace(
        go.Scatter(
            x=steps,
            y=failed,
            mode="lines+markers",
            line=dict(width=3),
            fill="tozeroy",
            name="Failed Agents",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=steps,
            y=recovery,
            mode="lines+markers",
            line=dict(width=3),
            fill="tozeroy",
            name="Recovery Events",
        ),
        row=2,
        col=1,
    )

    _add_event_lines(fig, events, row=1, col=1)
    _add_event_lines(fig, events, row=2, col=1)

    fig.update_yaxes(title_text="Count", row=1, col=1)
    fig.update_yaxes(title_text="Count", row=2, col=1)
    fig.update_xaxes(title_text="Simulation Step", row=2, col=1)

    fig.update_layout(
        template="plotly_dark",
        height=CHART_HEIGHT_LARGE,
        margin=dict(l=50, r=25, t=70, b=45),
        font=dict(family=FONT_FAMILY, size=13),
        showlegend=False,
        title=dict(text="Resilience Metrics", x=0.02, xanchor="left"),
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True, key="resilience_chart")


def agent_status_timeline(history: list, num_agents: int = 3) -> None:
    if not history or "agent_states" not in history[0]:
        st.info("No data yet.")
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
            elif status == "recovering":
                val = 3
            else:
                val = 0

            row.append(val)
        z.append(row)

    fig = go.Figure(
        data=go.Heatmap(
            x=steps,
            y=[f"Agent {i + 1}" for i in range(num_agents)],
            z=z,
            zmin=0,
            zmax=3,
            colorscale=[
                [0.0, "#ef4444"],
                [0.33, "#22c55e"],
                [0.66, "#3b82f6"],
                [1.0, "#f59e0b"],
            ],
            colorbar=dict(
                tickvals=[0, 1, 2, 3],
                ticktext=["Failed", "Active", "Reassigned", "Recovering"],
                title="State",
            ),
        )
    )

    fig.update_xaxes(title_text="Simulation Step")
    fig.update_yaxes(title_text="Agent")
    _base_layout(fig, "Agent Operational Timeline", CHART_HEIGHT_SMALL)
    st.plotly_chart(fig, use_container_width=True, key="agent_status_timeline")


def workload_chart(history: list, num_agents: int = 3) -> None:
    if not history or "task_loads" not in history[0]:
        st.info("No data yet.")
        return

    steps = [h["step"] for h in history]
    fig = go.Figure()

    for a in range(num_agents):
        loads = [h["task_loads"][a] if a < len(h["task_loads"]) else 0 for h in history]
        fig.add_trace(
            go.Scatter(
                x=steps,
                y=loads,
                mode="lines+markers",
                name=f"Agent {a + 1}",
                line=dict(width=3),
            )
        )

    fig.update_xaxes(title_text="Simulation Step")
    fig.update_yaxes(title_text="Zones Controlled")
    _base_layout(fig, "Task Reallocation / Workload Redistribution", CHART_HEIGHT_MEDIUM)
    st.plotly_chart(fig, use_container_width=True, key="workload_chart")


def recovery_time_chart(
    history: list,
    events: list | None = None,
    unsafe_threshold: float | None = None,
    target_temp: float | None = None,
    tolerance: float = 2.0,
) -> None:
    """
    Research chart: recovery latency after the first failure injection/confirmation.

    Recovery definition (simple + explainable):
      recovered when max(zone_temp) <= (target_temp + tolerance)
      OR (if target_temp is None) max(zone_temp) <= unsafe_threshold

    Y-axis is in simulation steps (poster-friendly and deterministic).
    """
    if not history:
        st.info("No data yet.")
        return

    events = events or []

    # Pick the first failure-related event step.
    failure_types = {
        "auto_failure_injected",
        "random_failure_injected",
        "manual_failure_injected",
        "agent_failed",
        "heartbeat_failure_detected",
    }
    failure_step = None
    for ev in events:
        if ev.get("type") in failure_types:
            failure_step = ev.get("step")
            break

    steps = [h.get("step", i) for i, h in enumerate(history)]
    temps = [h.get("temps", []) for h in history]

    if failure_step is None:
        st.info("No failure event found in event log for recovery-time chart.")
        return

    # Define the recovery boundary.
    if target_temp is not None:
        recovery_bound = float(target_temp) + float(tolerance)
    elif unsafe_threshold is not None:
        recovery_bound = float(unsafe_threshold)
    else:
        recovery_bound = None

    if recovery_bound is None:
        st.info("Need `target_temp` or `unsafe_threshold` to compute recovery time.")
        return

    recovered_step = None
    for s, tlist in zip(steps, temps):
        if s < failure_step:
            continue
        if not tlist:
            continue
        if max(tlist) <= recovery_bound:
            recovered_step = s
            break

    if recovered_step is None:
        recovery_latency = None
    else:
        recovery_latency = recovered_step - failure_step

    # Plot as a single-point bar (clean poster presentation).
    fig = go.Figure()
    if recovery_latency is None:
        fig.add_trace(go.Bar(x=["N/A"], y=[0], marker_color="rgba(245, 158, 11, 0.65)"))
    else:
        fig.add_trace(go.Bar(x=["Run 1"], y=[recovery_latency], marker_color="rgba(34, 197, 94, 0.75)"))

    fig.update_xaxes(title_text="Experiment")
    fig.update_yaxes(title_text="Recovery Time (steps)")
    _base_layout(fig, "Recovery Time After Failure", CHART_HEIGHT_SMALL)
    st.plotly_chart(fig, use_container_width=True, key="recovery_time_chart")


def consensus_decision_time_chart(history: list, events: list | None = None) -> None:
    """
    Research chart: consensus decision latency in steps.

    Defined as:
      (consensus_completed.step - heartbeat_failure_detected.step)
    for matching failures where:
      heartbeat_failure_detected.agent_id == consensus_completed.failed_agent
    """
    events = events or []
    if not history or not events:
        st.info("No data yet.")
        return

    hb_events = [e for e in events if e.get("type") == "heartbeat_failure_detected"]
    cons_events = [e for e in events if e.get("type") == "consensus_completed"]

    deltas = []
    for hb in hb_events:
        hb_step = hb.get("step")
        agent_id = hb.get("agent_id")
        if hb_step is None or agent_id is None:
            continue
        match = next(
            (c for c in cons_events if c.get("failed_agent") == agent_id and c.get("step") is not None),
            None,
        )
        if match:
            deltas.append(match["step"] - hb_step)

    if not deltas:
        st.info("No matching heartbeat->consensus events found for decision-time chart.")
        return

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(1, len(deltas) + 1)), y=deltas, mode="markers+lines", name="Decision latency"))
    fig.update_xaxes(title_text="Failure instance")
    fig.update_yaxes(title_text="Decision time (steps)")
    _base_layout(fig, "Consensus Decision Time (Heartbeat -> Consensus)", CHART_HEIGHT_SMALL)
    st.plotly_chart(fig, use_container_width=True, key="consensus_decision_time_chart")


def all_charts(
    history: list,
    num_zones: int = 3,
    unsafe_threshold: float | None = None,
    target_temp: float | None = None,
    events: list | None = None,
) -> None:
    c1, c2 = st.columns(2)
    with c1:
        temp_chart(
            history,
            num_zones=num_zones,
            unsafe_threshold=unsafe_threshold,
            target_temp=target_temp,
            events=events,
        )
    with c2:
        fan_speed_chart(history, num_zones=num_zones)

    c3, c4 = st.columns(2)
    with c3:
        fan_temp_chart(history, num_zones=num_zones, target_temp=target_temp)
    with c4:
        agent_status_timeline(history, num_agents=num_zones)

    c5, c6 = st.columns(2)
    with c5:
        consensus_decision_time_chart(history, events=events)
    with c6:
        recovery_time_chart(
            history,
            events=events,
            unsafe_threshold=unsafe_threshold,
            target_temp=target_temp,
        )

    c7, c8 = st.columns(2)
    with c7:
        workload_chart(history, num_agents=num_zones)
    with c8:
        resilience_chart(history, events=events)
