"""
Reusable UI components for the MAS simulation dashboard.

Zone cards, agent cards, control buttons, and status indicators
with consistent icons and styling.
"""

import streamlit as st

# Icons for the research prototype
ICONS = {
    "heat": "🔥",
    "fan": "🌀",
    "agent": "🤖",
    "temp": "🌡️",
    "heartbeat": "❤️",
    "kill_switch": "🛑",
    "recovery": "🔄",
    "play": "▶️",
    "pause": "⏸️",
    "step": "⏭️",
    "reset": "🔄",
    "inject": "💉",
    "unsafe": "⚠️",
}


def zone_card(zone_id: int, temp: float, fan_speed: int, heat_source: float,
              unsafe_threshold: float = 80.0) -> None:
    """
    Display a thermal zone with temp, fan speed, heat source.
    Color gradient from cool (blue) to hot (red) based on temp.
    """
    ratio = min(1.0, temp / unsafe_threshold) if unsafe_threshold > 0 else 0
    # RGB: blue (0) -> cyan -> green -> yellow -> red (1)
    r = int(255 * ratio)
    g = int(255 * (1 - ratio * 0.7))
    b = int(255 * (1 - ratio))
    r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
    bg = f"rgb({r},{g},{b})"
    fg = "white" if ratio > 0.5 else "black"

    st.markdown(
        f"""
        <div style="
            padding: 1rem; border-radius: 8px; margin: 0.5rem 0;
            background: {bg}; color: {fg}; font-weight: bold;
            border: 2px solid #333;
        ">
            <span style="font-size: 1.5rem;">{ICONS['temp']}</span> Zone {zone_id + 1}
            <br>Temp: <strong>{temp:.1f}°C</strong>
            <br><span style="font-size: 1.2rem;">{ICONS['fan']}</span> Fan: {fan_speed}/255
            <br><span style="font-size: 1.2rem;">{ICONS['heat']}</span> Heat: {heat_source:.1f}
        </div>
        """,
        unsafe_allow_html=True,
    )


def agent_card(zone_id: int, status: str, task_load: int, last_seen: int,
               current_step: int, heartbeat_timeout: int = 3,
               liveness_state: str | None = None) -> None:
    """Display agent status: active/failed/recovering, heartbeat, task load."""
    status_emoji = {"active": "🟢", "failed": "🔴", "recovering": "🟡"}.get(status, "⚪")
    dt = current_step - last_seen
    hb_ok = dt <= heartbeat_timeout and status != "failed"
    # Show a three-level heartbeat/liveness view.
    if liveness_state == "suspect":
        hb_icon = "💤"  # sleepy / suspect
    elif not hb_ok:
        hb_icon = "💔"
    else:
        hb_icon = "❤️"

    st.markdown(
        f"""
        <div style="
            padding: 0.8rem; border-radius: 6px; margin: 0.3rem 0;
            background: #1e1e2e; color: #cdd6f4; border-left: 4px solid
            {'#a6e3a1' if status == 'active' else '#f38ba8' if status == 'failed' else '#f9e2af'};
        ">
            {ICONS['agent']} <strong>Agent {zone_id + 1}</strong> {status_emoji} {status}
            <br>{hb_icon} Heartbeat | Load: {task_load} zone(s)
        </div>
        """,
        unsafe_allow_html=True,
    )


def control_buttons(ctrl) -> None:
    """Render Start, Pause, Step, Inject (chosen agent), Inject random, Trigger Unsafe."""
    cols = st.columns(6)
    buttons_config = [
        (ICONS["play"], "Start", "btn_start"),
        (ICONS["pause"], "Pause", "btn_pause"),
        (ICONS["step"], "Step", "btn_step"),
        (ICONS["inject"], "Fail chosen", "btn_inject"),
        (ICONS["inject"], "Fail random", "btn_inject_random"),
        (ICONS["unsafe"], "Trigger Unsafe", "btn_unsafe"),
    ]
    for col, (icon, label, key) in zip(cols, buttons_config):
        with col:
            if st.button(f"{icon} {label}", key=key, use_container_width=True):
                if key == "btn_start":
                    st.session_state.auto_run = True
                    st.rerun()
                elif key == "btn_pause":
                    st.session_state.auto_run = False
                    st.rerun()
                elif key == "btn_step":
                    ctrl.run_step()
                    st.rerun()
                elif key == "btn_inject":
                    agent_idx = st.session_state.get("inject_agent", 1)
                    ctrl.inject_failure(agent_idx)
                    ctrl.run_step()
                    st.rerun()
                elif key == "btn_inject_random":
                    ctrl.inject_failure_random()
                    ctrl.run_step()
                    st.rerun()
                elif key == "btn_unsafe":
                    ctrl.trigger_unsafe(0)
                    st.rerun()


def kill_switch_banner(active: bool) -> None:
    """Display kill-switch status prominently."""
    if active:
        st.error(f"{ICONS['kill_switch']} **KILL-SWITCH ACTIVE** — System shut down for safety.")
    else:
        st.success(f"✅ System operational")


def redistribution_log_entries(log: list, max_entries: int = 10) -> None:
    """Display recent redistribution events."""
    for entry in log[-max_entries:][::-1]:
        st.caption(
            f"{ICONS['recovery']} Step {entry['step']}: "
            f"Agent {entry['from_agent'] + 1} → Agent {entry['to_agent'] + 1}"
        )


def simple_agent_view(model, redistribution_log: list) -> None:
    """
    Kid-friendly view: big agent cards that clearly show who is working,
    who failed, and when others take over. Easy to understand at a glance.
    """
    agents = model.thermal_agents
    n = len(agents)

    # One big card per agent in a horizontal row
    cols = st.columns(n)
    for i, agent in enumerate(agents):
        with cols[i]:
            if agent.status == "active":
                emoji = "🤖"
                label = "Working!"
                color = "#22c55e"
                msg = "This robot is watching the temperature and controlling the fan."
                if agent.task_load > 1:
                    msg = f"This robot is helping with **{agent.task_load}** zones!"
            elif agent.status == "failed":
                emoji = "🤖💔"
                label = "Stopped working"
                color = "#ef4444"
                msg = "This robot stopped. The other robots are doing its job now."
            else:
                emoji = "🤖🔄"
                label = "Getting better"
                color = "#eab308"
                msg = "This robot is recovering."

            st.markdown(
                f"""
                <div style="
                    text-align: center; padding: 1.5rem; border-radius: 12px;
                    background: {'#fef2f2' if agent.status == 'failed' else '#f0fdf4' if agent.status == 'active' else '#fefce8'};
                    border: 4px solid {color}; margin: 0.5rem 0;
                ">
                    <div style="font-size: 4rem;">{emoji}</div>
                    <div style="font-size: 1.4rem; font-weight: bold; color: {color};">
                        Robot {i + 1}
                    </div>
                    <div style="font-size: 1.1rem; margin: 0.5rem 0;">{label}</div>
                    <div style="font-size: 0.95rem; color: #374151;">{msg}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Simple story line for kids
    failed = [a for a in agents if a.status == "failed"]
    if failed and redistribution_log:
        last = redistribution_log[-1]
        from_id = last["from_agent"] + 1
        to_id = last["to_agent"] + 1
        st.info(
            f"**What happened:** Robot **{from_id}** stopped working. "
            f"So Robot **{to_id}** is now doing Robot {from_id}'s job too! "
            "The team shares the work when someone stops."
        )
    elif failed:
        st.warning(
            f"**What happened:** One of the robots stopped. "
            "The others will take over its job when you press **Step**."
        )

    if model.system_shutdown:
        st.error(
            "**Safety stop:** Things got too hot or too many robots stopped, "
            "so the system turned off to stay safe."
        )


def _controller_of_zone(model, zone_id: int):
    """Return the agent that controls this zone (has zone_id in assigned_heat_sources)."""
    for a in model.thermal_agents:
        if zone_id in a.assigned_heat_sources:
            return a
    return None


def simulation_animation(model, unsafe_threshold: float = 80.0, target_temp: float = 35.0) -> None:
    """
    Child-friendly: lots of motion, minimal text. Robot controls fan to reach target temp.
    Animated takeover when one robot switches to help another zone.
    """
    agents = model.thermal_agents
    n = len(agents)
    log = getattr(model, "redistribution_log", [])

    st.markdown(
        """
        <style>
        @keyframes fan-rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .robot-alive { animation: bounce 1.2s ease-in-out infinite; }
        @keyframes bounce { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
        .heat-hot { animation: glow 0.8s ease-in-out infinite; }
        @keyframes glow { 0%,100% { opacity: 1; filter: brightness(1.2); } 50% { opacity: 0.9; filter: brightness(1.5); } }
        .arrow-move { animation: slide 0.8s ease-in-out infinite; }
        @keyframes slide { 0%,100% { transform: translateX(0); opacity: 1; } 50% { transform: translateX(4px); opacity: 0.8; } }
        </style>
        """,
        unsafe_allow_html=True,
    )

    zone_html = []
    for z in range(n):
        controller = _controller_of_zone(model, z)
        agent = agents[z]
        temp = model.zone_temperatures.get(z, agent.temperature)
        # Each zone has its own physical fan; speed comes from model.fan_speeds.
        fan_speed = model.fan_speeds.get(z, 0)
        heat = model.heat_sources.get(z, 5)

        ratio = min(1.0, temp / unsafe_threshold) if unsafe_threshold > 0 else 0
        r = int(255 * ratio)
        g = int(255 * (1 - ratio * 0.7))
        b = int(255 * (1 - ratio))
        r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
        heat_bg = f"rgb({r},{g},{b})"
        fg = "white" if ratio > 0.5 else "black"

        robot_icon = "🤖" if agent.status == "active" else "😵"
        robot_class = "robot-alive" if agent.status == "active" else ""
        fan_spinning = fan_speed > 0 and controller and controller.status == "active"
        fan_dur = max(0.25, 1.4 - (fan_speed / 255) * 1.15) if fan_spinning else 1
        fan_style = f"font-size:2.2rem;margin:6px 0;display:inline-block;" + (f"animation:fan-rotate {fan_dur}s linear infinite;" if fan_spinning else "")
        heat_class = "heat-hot" if ratio > 0.6 else ""
        bar_pct = min(100, (fan_speed / 255) * 100)

        controlled_by = ""
        if controller and controller.zone_id != z:
            cid = controller.zone_id
            controlled_by = (
                f'<div style="margin-top:6px;padding:8px;background:linear-gradient(90deg,#064e3b,#065f46);'
                'border-radius:10px;font-size:0.9rem;color:#6ee7b7;display:flex;align-items:center;justify-content:center;gap:6px;">'
                f'<span class="robot-alive">🤖{cid+1}</span>'
                '<span class="arrow-move">➡️</span><span class="arrow-move">➡️</span>'
                '<span>cooling!</span>'
                '</div>'
            )

        zone_html.append(
            f'<div style="flex:1;min-width:130px;text-align:center;padding:1rem;background:linear-gradient(180deg,#1e293b,#0f172a);'
            f'border-radius:16px;margin:8px;border:4px solid {heat_bg};color:#e2e8f0;box-shadow:0 4px 12px rgba(0,0,0,0.3);">'
            f'<div class="{robot_class}" style="font-size:3.5rem;">{robot_icon}</div>'
            f'<div style="{fan_style}">🌀</div>'
            f'<div style="height:12px;background:#334155;border-radius:6px;overflow:hidden;margin:6px 0;">'
            f'<div style="height:100%;width:{bar_pct}%;background:linear-gradient(90deg,#22c55e,#4ade80);border-radius:6px;transition:width 0.3s;"></div></div>'
            f'<div class="{heat_class}" style="margin:6px 0;padding:8px;border-radius:10px;background:{heat_bg};color:{fg};font-size:1.2rem;font-weight:bold;">'
            f'🌡️ {temp:.0f}°</div>'
            f'<div style="font-size:0.75rem;color:#94a3b8;">goal: {target_temp:.0f}°</div>'
            f'<div style="margin-top:4px;font-size:1.5rem;">🔥</div>'
            f'{controlled_by}</div>'
        )

    zones_inner = "".join(zone_html)

    # Floating takeover banner: Robot X → Zone Y (animated)
    takeover_viz = ""
    if log:
        last = log[-1]
        from_z, to_z = last["from_agent"], last["to_agent"]
        takeover_viz = (
            '<div style="display:flex;justify-content:center;margin-bottom:12px;">'
            '<div style="display:flex;align-items:center;gap:10px;background:linear-gradient(90deg,#064e3b,#065f46);'
            'padding:10px 20px;border-radius:24px;box-shadow:0 4px 12px rgba(0,0,0,0.3);">'
            f'<span class="robot-alive" style="font-size:1.8rem;">🤖{to_z+1}</span>'
            '<span class="arrow-move" style="font-size:1.2rem;">➡️</span>'
            '<span class="arrow-move" style="font-size:1.2rem;">➡️</span>'
            f'<span style="font-size:1.1rem;">Zone {from_z+1}</span>'
            '</div></div>'
        )

    overlay = ""
    if model.system_shutdown:
        overlay = (
            '<div style="position:absolute;inset:0;background:rgba(220,38,38,0.92);border-radius:16px;'
            'display:flex;flex-direction:column;align-items:center;justify-content:center;font-weight:bold;color:white;">'
            '<div style="font-size:4rem;animation:glow 0.5s infinite;">🛑</div>'
            '<div style="font-size:1.8rem;">STOP</div></div>'
        )

    st.markdown(
        f'<div style="position:relative;padding:1.5rem;border-radius:16px;background:#0f172a;margin:1rem 0;">'
        f'{takeover_viz}'
        f'<div style="display:flex;flex-wrap:wrap;justify-content:center;align-items:stretch;">{zones_inner}</div>'
        f'{overlay}</div>',
        unsafe_allow_html=True,
    )
