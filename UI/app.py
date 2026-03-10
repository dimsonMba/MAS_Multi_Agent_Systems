"""
MAS Simulation Dashboard — UI layer for decentralized failure recovery.

Run with: streamlit run UI/app.py
"""

import sys
from pathlib import Path

# Ensure project root is on path when running from UI/
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import time

from UI.simulation_controller import SimulationController
from UI.components import zone_card, control_buttons, simple_agent_view, simulation_animation
from UI.state_view import render_mas_state
from UI.charts import all_charts

# Page config
st.set_page_config(
    page_title="MAS Thermal Simulation",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🤖 MAS Thermal Simulation — Decentralized Failure Recovery")
st.caption("Research prototype: heat sources, fans, agents, heartbeat, redistribution, kill-switch")

# Sidebar: Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    num_agents = st.number_input("Number of agents", 1, 10, 3)
    initial_temps = [
        st.number_input(f"Zone {i+1} initial temp (°C)", 0.0, 100.0, 30.0 + i * 5.0, key=f"init_temp_{i}")
        for i in range(min(num_agents, 10))
    ]
    if len(initial_temps) < num_agents:
        initial_temps.extend([30.0] * (num_agents - len(initial_temps)))
    initial_temps = initial_temps[:num_agents]

    failure_step = st.number_input("Failure injection step", 0, 500, 20)
    unsafe_temp_threshold = st.number_input("Unsafe temp threshold (°C)", 50.0, 150.0, 80.0)
    target_temp = st.number_input("Target temp (°C)", 20.0, 60.0, 35.0)
    num_steps = st.number_input("Auto-run steps per tick", 1, 100, 1)

    st.divider()
    st.subheader("Manual Overrides")
    override_zone = st.selectbox("Zone to override", list(range(num_agents)), format_func=lambda x: f"Zone {x+1}")
    override_temp = st.number_input("Override temp (°C)", 0.0, 150.0, 50.0, key="override_temp")
    override_fan = st.slider("Override fan speed", 0, 255, 128, key="override_fan")
    override_heat = st.number_input("Override heat source", 0.0, 50.0, 5.0, key="override_heat")
    if st.button("Apply overrides"):
        if "ctrl" in st.session_state:
            st.session_state.ctrl.set_zone_temp(override_zone, override_temp)
            st.session_state.ctrl.set_fan_speed(override_zone, override_fan)
            st.session_state.ctrl.set_heat_source(override_zone, override_heat)
            st.success("Applied")
        st.rerun()

    inject_agent = st.selectbox("Agent to inject failure", list(range(num_agents)), min(1, num_agents - 1), format_func=lambda x: f"Agent {x+1}")
    st.session_state["inject_agent"] = inject_agent
    st.caption("Use **Fail chosen** to fail this agent; **Fail random** to fail any random agent. At the step set above, one random agent also fails automatically.")

# Initialize or reset controller when config changes (e.g. number of agents)
def get_config():
    return {
        "num_agents": num_agents,
        "width": 5,
        "height": 5,
        "initial_temps": initial_temps[:num_agents],
        "failure_step": int(failure_step),
        "unsafe_temp_threshold": unsafe_temp_threshold,
        "target_temp": target_temp,
    }

config_now = get_config()


def config_changed(stored, current):
    """True if any config value changed (so we need to reset)."""
    if stored is None:
        return True
    n = current.get("num_agents", 3)
    if stored.get("num_agents") != n:
        return True
    old_temps = stored.get("initial_temps", [])[:n]
    new_temps = current.get("initial_temps", [])[:n]
    if len(old_temps) != len(new_temps) or any(a != b for a, b in zip(old_temps, new_temps)):
        return True
    if stored.get("target_temp") != current.get("target_temp"):
        return True
    if stored.get("unsafe_temp_threshold") != current.get("unsafe_temp_threshold"):
        return True
    if stored.get("failure_step") != current.get("failure_step"):
        return True
    return False


need_reset = (
    "ctrl" not in st.session_state
    or config_changed(st.session_state.get("ctrl_config"), config_now)
)
if need_reset:
    st.session_state.ctrl = SimulationController(**config_now)
    st.session_state.ctrl_config = config_now.copy()
    if "auto_run" in st.session_state:
        st.session_state.auto_run = False

if "auto_run" not in st.session_state:
    st.session_state.auto_run = False

ctrl = st.session_state.ctrl
model = ctrl.model

# Reset button in sidebar
if st.sidebar.button("🔄 Reset simulation"):
    st.session_state.ctrl = SimulationController(**get_config())
    st.session_state.auto_run = False
    st.rerun()

# System controls: full-width horizontal bar at top
st.subheader("🎮 System Controls")
control_buttons(ctrl)
st.divider()

# Tabs: Simulation (animated), Dashboard, Simple view
tab_sim, tab_dashboard, tab_simple = st.tabs([
    "🎬 Simulation — Fans, robots, heat",
    "📊 Dashboard",
    "👀 Simple view — See the robots",
])

with tab_sim:
    st.subheader("🎬 Simulation")
    simulation_animation(model, model.unsafe_temp_threshold, model.target_temp)

with tab_dashboard:
    # Main layout: 3 columns — left: summary, middle: thermal zones, right: MAS state
    col_left, col_mid, col_right = st.columns([1, 2, 1])

    with col_left:
        st.subheader("📋 Summary")
        st.metric("Step", model.current_step)
        st.metric("Failed agents", len([a for a in model.thermal_agents if a.status == "failed"]))
        st.metric("Recovery events", model.recovery_events)

    with col_mid:
        st.subheader("🌡️ Thermal Zones")
        for i in range(model.num_agents):
            a = model.thermal_agents[i]
            zone_card(
                zone_id=i,
                temp=a.temperature,
                fan_speed=a.fan_speed,
                heat_source=model.heat_sources.get(i, 5),
                unsafe_threshold=model.unsafe_temp_threshold,
            )

    with col_right:
        render_mas_state(model, model.heartbeat_timeout)

    # Bottom: Charts
    st.divider()
    st.subheader("📊 Charts")
    all_charts(ctrl.history, model.num_agents)

with tab_simple:
    st.subheader("👀 What’s happening to the robots?")
    st.caption("Each robot watches one zone. If a robot stops, the others take over its job.")
    simple_agent_view(model, getattr(model, "redistribution_log", []))

# Auto-run: one step per rerun when Start is active
if st.session_state.auto_run and not model.system_shutdown:
    for _ in range(num_steps):
        ctrl.run_step()
        if model.system_shutdown:
            break
    time.sleep(0.3)
    st.rerun()

# Charts appear only in Dashboard tab (moved inside tab_dashboard above)
