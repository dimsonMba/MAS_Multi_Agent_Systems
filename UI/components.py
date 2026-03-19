"""
Reusable UI components for the MAS research dashboard.

Industrial/research-oriented components:
- system status badge
- thermal zone panels
- agent state cards
- supervisor state card
- control bar
- simplified public-demo view
"""

import streamlit as st

ICONS = {
    "temp": "🌡️",
    "fan": "🌀",
    "heat": "🔥",
    "agent": "🤖",
    "heartbeat": "❤️",
    "warning": "⚠️",
    "critical": "🚨",
    "shutdown": "🛑",
    "recovery": "🔄",
    "supervisor": "🛡️",
    "play": "▶️",
    "pause": "⏸️",
    "step": "⏭️",
    "inject": "💉",
}


def _fan_pct(pwm: int) -> float:
    return (max(0, min(255, pwm)) / 255.0) * 100.0


def system_status_badge(model) -> None:
    """Render overall system health badge."""
    max_temp = max(model.zone_temperatures.values()) if model.zone_temperatures else 0.0
    unsafe = getattr(model, "unsafe_temp_threshold", 80.0)
    warning = unsafe * 0.85

    if model.system_shutdown:
        label = "System Status: Emergency Shutdown"
        color = "#ef4444"
    elif max_temp >= unsafe:
        label = "System Status: Critical Thermal Condition"
        color = "#dc2626"
    elif max_temp >= warning:
        label = "System Status: Warning"
        color = "#f59e0b"
    else:
        label = "System Status: Operational"
        color = "#22c55e"

    st.markdown(
        f"""
        <div style="
            margin: 0.25rem 0 0.5rem 0;
            padding: 0.7rem 1rem;
            border-radius: 12px;
            background: {color};
            color: white;
            font-weight: 800;
            font-size: 1rem;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.18);
        ">
            {label}
        </div>
        """,
        unsafe_allow_html=True,
    )


def supervisor_card(model) -> None:
    """Research/industrial supervisor panel."""
    unsafe = getattr(model, "unsafe_temp_threshold", 80.0)
    temps = list(getattr(model, "zone_temperatures", {}).values())
    max_temp = max(temps) if temps else 0.0
    warning_at = unsafe * 0.85

    if getattr(model, "system_shutdown", False):
        state = "SHUTDOWN"
        color = "#ef4444"
        msg = "Unsafe system condition detected. Emergency shutdown has been activated."
    elif max_temp >= unsafe:
        state = "CRITICAL"
        color = "#dc2626"
        msg = "A zone has exceeded the unsafe thermal threshold."
    elif max_temp >= warning_at:
        state = "WARNING"
        color = "#f59e0b"
        msg = "Thermal conditions are approaching the unsafe threshold."
    else:
        state = "NORMAL"
        color = "#22c55e"
        msg = "Supervisory safety monitoring is active."

    st.markdown(
        f"""
        <div style="
            padding: 0.95rem;
            border-radius: 12px;
            margin: 0.35rem 0 0.8rem 0;
            background: #0f172a;
            color: #e5e7eb;
            border: 2px solid {color};
            box-shadow: 0 6px 18px rgba(0,0,0,0.22);
        ">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;">
                <div style="font-size:1rem;font-weight:800;">{ICONS['supervisor']} Supervisor</div>
                <div style="
                    padding:4px 10px;
                    border-radius:999px;
                    background:{color};
                    color:white;
                    font-weight:900;
                    font-size:0.85rem;
                ">
                    {state}
                </div>
            </div>
            <div style="margin-top:8px;font-size:0.94rem;line-height:1.35;">
                <div><strong>Hottest zone:</strong> {max_temp:.1f} °C</div>
                <div style="margin-top:6px;">{msg}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def zone_card(
    zone_id: int,
    temp: float,
    fan_speed: int,
    heat_source: float,
    unsafe_threshold: float = 80.0,
    target_temp: float = 35.0,
) -> None:
    """Industrial thermal zone card (no raw HTML; always renders)."""
    fan_pct = _fan_pct(fan_speed)

    if temp >= unsafe_threshold:
        banner = "🚨 UNSAFE"
    elif temp >= unsafe_threshold * 0.85:
        banner = "⚠️ WARNING"
    else:
        banner = "✅ NOMINAL"

    with st.container():
        st.markdown(f"### {ICONS['temp']} Zone {zone_id + 1}  \n{banner}")

        c1, c2 = st.columns(2)
        with c1:
            st.metric("Current Temperature (°C)", f"{temp:.1f}")
        with c2:
            st.metric("Target Temperature (°C)", f"{target_temp:.1f}")

        c3, c4 = st.columns(2)
        with c3:
            st.metric("Fan Command", f"{fan_pct:.0f}% ({fan_speed}/255)")
            st.progress(int(max(0, min(100, fan_pct))))
        with c4:
            st.metric("Heat Input", f"{heat_source:.1f}")

        st.divider()


def agent_card(
    zone_id: int,
    status: str,
    task_load: int,
    last_seen: int,
    current_step: int,
    heartbeat_timeout: int = 3,
    liveness_state: str | None = None,
) -> None:
    """Render agent operational and liveness state."""
    if status == "failed":
        border = "#ef4444"
        badge = "FAILED"
    elif status == "recovering":
        border = "#f59e0b"
        badge = "RECOVERING"
    else:
        border = "#22c55e"
        badge = "ACTIVE"

    dt = current_step - last_seen
    if liveness_state == "suspect":
        hb_label = "Suspect"
        hb_icon = "💤"
    elif status == "failed" or dt > heartbeat_timeout:
        hb_label = "Lost"
        hb_icon = "💔"
    else:
        hb_label = "Healthy"
        hb_icon = "❤️"

    st.markdown(
        f"""
        <div style="
            background:#111827;
            color:#e5e7eb;
            border-left:5px solid {border};
            border-radius:10px;
            padding:0.85rem;
            margin:0.35rem 0;
        ">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="font-weight:800;">{ICONS['agent']} Agent {zone_id + 1}</div>
                <div style="
                    background:{border};
                    color:white;
                    padding:3px 9px;
                    border-radius:999px;
                    font-size:0.78rem;
                    font-weight:800;
                ">
                    {badge}
                </div>
            </div>
            <div style="margin-top:8px;font-size:0.92rem;">
                <div>{hb_icon} <strong>Liveness:</strong> {hb_label}</div>
                <div><strong>Task load:</strong> {task_load} zone(s)</div>
                <div><strong>Last heartbeat step:</strong> {last_seen}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kill_switch_banner(active: bool) -> None:
    """Kill-switch banner."""
    if active:
        st.error("Emergency shutdown active. The supervisory kill-switch has halted system operation.")
    else:
        st.success("Supervisory safety system reports normal operation.")


def redistribution_log_entries(log: list, max_entries: int = 10) -> None:
    """Redistribution log entries."""
    if not log:
        st.info("No redistribution events recorded.")
        return

    for entry in log[-max_entries:][::-1]:
        zones = entry.get("zones", [])
        zone_text = ", ".join([f"Zone {z + 1}" for z in zones]) if zones else "N/A"
        st.caption(
            f"{ICONS['recovery']} Step {entry['step']}: "
            f"Agent {entry['from_agent'] + 1} → Agent {entry['to_agent'] + 1} | "
            f"Zones reassigned: {zone_text}"
        )


def control_buttons(ctrl) -> None:
    """Primary control bar."""
    cols = st.columns(6)
    labels = [
        (ICONS["play"], "Start", "start"),
        (ICONS["pause"], "Pause", "pause"),
        (ICONS["step"], "Step", "step"),
        (ICONS["inject"], "Fail Chosen", "fail_chosen"),
        (ICONS["inject"], "Fail Random", "fail_random"),
        (ICONS["warning"], "Trigger Unsafe", "unsafe"),
    ]

    for col, (icon, label, action) in zip(cols, labels):
        with col:
            if st.button(f"{icon} {label}", key=f"btn_{action}", use_container_width=True):
                if action == "start":
                    st.session_state.auto_run = True
                    st.rerun()
                elif action == "pause":
                    st.session_state.auto_run = False
                    st.rerun()
                elif action == "step":
                    ctrl.run_step()
                    st.rerun()
                elif action == "fail_chosen":
                    agent_idx = st.session_state.get("inject_agent", 0)
                    ctrl.inject_failure(agent_idx)
                    ctrl.run_step()
                    st.rerun()
                elif action == "fail_random":
                    ctrl.inject_failure_random()
                    ctrl.run_step()
                    st.rerun()
                elif action == "unsafe":
                    ctrl.trigger_unsafe(0)
                    ctrl.run_step()
                    st.rerun()


def simple_agent_view(model, redistribution_log: list) -> None:
    """Simplified demonstration view for non-technical audiences."""
    agents = model.thermal_agents
    cols = st.columns(len(agents))

    for i, agent in enumerate(agents):
        with cols[i]:
            if agent.status == "active":
                emoji = "🤖"
                label = "Available"
                color = "#22c55e"
                msg = "This agent is actively regulating its assigned zone."
                if agent.task_load > 1:
                    msg = f"This agent is currently supporting {agent.task_load} zones."
            elif agent.status == "failed":
                emoji = "🤖💔"
                label = "Unavailable"
                color = "#ef4444"
                msg = "This agent has failed and its workload must be reassigned."
            else:
                emoji = "🤖🔄"
                label = "Recovering"
                color = "#f59e0b"
                msg = "This agent is in a recovery state."

            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    padding:1.3rem;
                    border-radius:14px;
                    background:#f8fafc;
                    border:4px solid {color};
                    margin:0.5rem 0;
                ">
                    <div style="font-size:3.6rem;">{emoji}</div>
                    <div style="font-size:1.2rem;font-weight:800;color:{color};">Agent {i + 1}</div>
                    <div style="margin-top:0.4rem;font-weight:700;">{label}</div>
                    <div style="margin-top:0.45rem;font-size:0.92rem;color:#334155;">{msg}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if redistribution_log:
        last = redistribution_log[-1]
        from_id = last["from_agent"] + 1
        to_id = last["to_agent"] + 1
        st.info(
            f"Latest reassignment: Agent {from_id} failed, and Agent {to_id} assumed its workload."
        )

    if model.system_shutdown:
        st.error("The simulation entered emergency shutdown because a safety threshold was exceeded.")


def _controller_of_zone(model, zone_id: int):
    """Return the agent currently controlling the given zone."""
    for agent in model.thermal_agents:
        if zone_id in getattr(agent, "assigned_heat_sources", []):
            return agent
    return None


def simulation_animation(model, unsafe_threshold: float = 80.0, target_temp: float = 35.0) -> None:
    """
    Visual simulation panel.

    Kept visually engaging, but framed as an operational visualization rather than a toy view.
    """
    agents = model.thermal_agents
    n = len(agents)
    log = getattr(model, "redistribution_log", [])

    st.markdown(
        """
        <style>
        @keyframes fan-rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .agent-active { animation: bounce 1.2s ease-in-out infinite; }
        @keyframes bounce { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
        .heat-alert { animation: glow 0.8s ease-in-out infinite; }
        @keyframes glow { 0%,100% { opacity: 1; filter: brightness(1.15); } 50% { opacity: 0.92; filter: brightness(1.45); } }
        .move-arrow { animation: slide 0.8s ease-in-out infinite; }
        @keyframes slide { 0%,100% { transform: translateX(0); opacity: 1; } 50% { transform: translateX(4px); opacity: 0.78; } }
        .supervisor-pulse { animation: sup-pulse 1.2s ease-in-out infinite; }
        @keyframes sup-pulse { 0%,100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.05); opacity: 0.92; } }
        </style>
        """,
        unsafe_allow_html=True,
    )

    zone_html = []
    for z in range(n):
        controller = _controller_of_zone(model, z)
        owner = agents[z]
        temp = model.zone_temperatures.get(z, owner.temperature)
        fan_speed = model.fan_speeds.get(z, 0)
        ratio = min(1.0, temp / unsafe_threshold) if unsafe_threshold > 0 else 0.0

        r = int(255 * ratio)
        g = int(255 * (1 - ratio * 0.7))
        b = int(255 * (1 - ratio))
        heat_bg = f"rgb({max(0,min(255,r))},{max(0,min(255,g))},{max(0,min(255,b))})"
        fg = "white" if ratio > 0.5 else "black"

        robot_icon = "🤖" if owner.status != "failed" else "⚙️"
        robot_class = "agent-active" if owner.status == "active" else ""
        spinning = fan_speed > 0 and controller and controller.status == "active"
        fan_dur = max(0.25, 1.4 - (fan_speed / 255.0) * 1.15) if spinning else 1
        fan_style = "font-size:2.2rem;margin:6px 0;display:inline-block;"
        if spinning:
            fan_style += f"animation:fan-rotate {fan_dur}s linear infinite;"

        heat_class = "heat-alert" if temp >= unsafe_threshold * 0.85 else ""
        bar_pct = min(100, (fan_speed / 255.0) * 100.0)

        controlled_by = ""
        if controller and controller.zone_id != z:
            cid = controller.zone_id
            controlled_by = (
                f'<div style="margin-top:6px;padding:8px;background:linear-gradient(90deg,#0f766e,#115e59);'
                'border-radius:10px;font-size:0.88rem;color:#ccfbf1;display:flex;align-items:center;justify-content:center;gap:6px;">'
                f'<span class="agent-active">Controller {cid + 1}</span>'
                '<span class="move-arrow">➡️</span><span>reassigned support</span>'
                '</div>'
            )

        zone_html.append(
            f'<div style="flex:1;min-width:145px;text-align:center;padding:1rem;background:linear-gradient(180deg,#1e293b,#0f172a);'
            f'border-radius:16px;margin:8px;border:4px solid {heat_bg};color:#e2e8f0;box-shadow:0 4px 12px rgba(0,0,0,0.28);">'
            f'<div class="{robot_class}" style="font-size:3.2rem;">{robot_icon}</div>'
            f'<div style="{fan_style}">🌀</div>'
            f'<div style="height:12px;background:#334155;border-radius:6px;overflow:hidden;margin:6px 0;">'
            f'<div style="height:100%;width:{bar_pct}%;background:linear-gradient(90deg,#22c55e,#4ade80);border-radius:6px;"></div></div>'
            f'<div class="{heat_class}" style="margin:6px 0;padding:8px;border-radius:10px;background:{heat_bg};color:{fg};font-size:1.2rem;font-weight:bold;">'
            f'🌡️ {temp:.0f}°C</div>'
            f'<div style="font-size:0.75rem;color:#94a3b8;">Target: {target_temp:.0f}°C</div>'
            f'<div style="margin-top:4px;font-size:1.4rem;">🔥</div>'
            f'{controlled_by}</div>'
        )

    takeover_viz = ""
    if log:
        last = log[-1]
        from_z = last["from_agent"]
        to_z = last["to_agent"]
        takeover_viz = (
            '<div style="display:flex;justify-content:center;margin-bottom:12px;">'
            '<div style="display:flex;align-items:center;gap:10px;background:linear-gradient(90deg,#0f766e,#115e59);'
            'padding:10px 20px;border-radius:24px;box-shadow:0 4px 12px rgba(0,0,0,0.25);color:#ecfeff;">'
            f'<span class="agent-active" style="font-size:1.15rem;font-weight:700;">Agent {to_z + 1}</span>'
            '<span class="move-arrow" style="font-size:1.1rem;">➡️</span>'
            f'<span style="font-size:1rem;">assumed workload from Agent {from_z + 1}</span>'
            '</div></div>'
        )

    overlay = ""
    if model.system_shutdown:
        overlay = (
            '<div style="position:absolute;inset:0;background:rgba(220,38,38,0.92);border-radius:16px;'
            'display:flex;flex-direction:column;align-items:center;justify-content:center;font-weight:bold;color:white;">'
            '<div style="font-size:4rem;">🛑</div>'
            '<div style="font-size:1.7rem;">Emergency Shutdown</div></div>'
        )

    temps = list(getattr(model, "zone_temperatures", {}).values())
    max_temp = max(temps) if temps else 0.0
    warning_at = unsafe_threshold * 0.85

    if model.system_shutdown:
        sup_color = "#ef4444"
        sup_text = "Emergency shutdown active"
    elif max_temp >= unsafe_threshold:
        sup_color = "#dc2626"
        sup_text = "Critical thermal condition detected"
    elif max_temp >= warning_at:
        sup_color = "#f59e0b"
        sup_text = "Thermal warning threshold reached"
    else:
        sup_color = "#22c55e"
        sup_text = "Supervisory monitoring active"

    supervisor_overlay = (
        f'<div style="position:absolute;left:14px;top:14px;background:rgba(11,18,32,0.95);'
        f'border:2px solid {sup_color};border-radius:14px;padding:10px 12px;max-width:250px;'
        'color:#e5e7eb;box-shadow:0 6px 18px rgba(0,0,0,0.22);">'
        f'<div class="supervisor-pulse" style="font-weight:900;">🛡️ Supervisor</div>'
        f'<div style="margin-top:6px;font-size:0.9rem;">{sup_text}</div>'
        f'<div style="margin-top:4px;font-size:0.85rem;color:#9ca3af;">Max temp: {max_temp:.1f} °C</div>'
        '</div>'
    )

    st.markdown(
        f'<div style="position:relative;padding:1.5rem;border-radius:16px;background:#0f172a;margin:1rem 0;">'
        f'{supervisor_overlay}'
        f'{takeover_viz}'
        f'<div style="display:flex;flex-wrap:wrap;justify-content:center;align-items:stretch;">{"".join(zone_html)}</div>'
        f'{overlay}</div>',
        unsafe_allow_html=True,
    )
