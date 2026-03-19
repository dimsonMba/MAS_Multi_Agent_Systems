"""
MAS Research Dashboard — decentralized thermal resilience simulation.

Run with:
    streamlit run UI/app.py
"""

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from UI.simulation_controller import SimulationController
from UI.components import (
    zone_card,
    control_buttons,
    simulation_animation,
    simple_agent_view,
    system_status_badge,
)
from UI.state_view import render_mas_state
from UI.charts import all_charts

# ----------------------------------------------------
# Page config
# ----------------------------------------------------
st.set_page_config(
    page_title="MAS Thermal Resilience Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("MAS Thermal Resilience Dashboard")
st.caption(
    "Research prototype for decentralized thermal regulation, heartbeat-based failure detection, "
    "consensus-driven reassignment, and supervisory safety shutdown."
)

# ----------------------------------------------------
# Sidebar configuration
# ----------------------------------------------------
with st.sidebar:
    st.header("Configuration")

    num_agents = st.number_input("Number of thermal agents", 1, 10, 3)

    initial_temps = [
        st.number_input(
            f"Zone {i+1} initial temperature (°C)",
            min_value=0.0,
            max_value=150.0,
            value=30.0 + i * 5.0,
            key=f"init_temp_{i}",
        )
        for i in range(min(num_agents, 10))
    ]
    if len(initial_temps) < num_agents:
        initial_temps.extend([30.0] * (num_agents - len(initial_temps)))
    initial_temps = initial_temps[:num_agents]

    failure_step = st.number_input("Scheduled failure injection step", 0, 500, 20)
    unsafe_temp_threshold = st.number_input("Unsafe temperature threshold (°C)", 40.0, 200.0, 80.0)
    target_temp = st.number_input("Target temperature (°C)", 10.0, 80.0, 35.0)
    num_steps = st.number_input("Auto-run steps per refresh", 1, 100, 1)
    random_seed = st.number_input("Random seed", 0, 999999, 42)

    st.divider()
    st.subheader("Manual Zone Overrides")

    override_zone = st.selectbox(
        "Zone to override",
        list(range(num_agents)),
        format_func=lambda x: f"Zone {x + 1}",
    )
    override_temp = st.number_input("Override temperature (°C)", 0.0, 200.0, 50.0, key="override_temp")
    override_fan = st.slider("Override fan PWM", 0, 255, 128, key="override_fan")
    override_heat = st.number_input("Override heat input", 0.0, 100.0, 5.0, key="override_heat")

    if st.button("Apply overrides", use_container_width=True):
        if "ctrl" in st.session_state:
            st.session_state.ctrl.set_zone_temp(override_zone, override_temp)
            st.session_state.ctrl.set_fan_speed(override_zone, override_fan)
            st.session_state.ctrl.set_heat_source(override_zone, override_heat)
            st.success("Overrides applied.")
        st.rerun()

    st.divider()
    st.subheader("Failure Injection")

    inject_agent = st.selectbox(
        "Agent to fail",
        list(range(num_agents)),
        index=min(1, num_agents - 1),
        format_func=lambda x: f"Agent {x + 1}",
    )
    st.session_state["inject_agent"] = inject_agent

    st.caption(
        "Use the control bar to inject a chosen failure, a random failure, or an unsafe thermal condition."
    )


# ----------------------------------------------------
# Config helpers
# ----------------------------------------------------
def get_config():
    return {
        "num_agents": int(num_agents),
        "width": 5,
        "height": 5,
        "initial_temps": initial_temps[:num_agents],
        "failure_step": int(failure_step),
        "unsafe_temp_threshold": float(unsafe_temp_threshold),
        "target_temp": float(target_temp),
        "random_seed": int(random_seed),
    }


def config_changed(stored, current):
    if stored is None:
        return True

    keys = [
        "num_agents",
        "failure_step",
        "unsafe_temp_threshold",
        "target_temp",
        "random_seed",
    ]
    for key in keys:
        if stored.get(key) != current.get(key):
            return True

    old_temps = stored.get("initial_temps", [])
    new_temps = current.get("initial_temps", [])
    if len(old_temps) != len(new_temps):
        return True
    if any(a != b for a, b in zip(old_temps, new_temps)):
        return True

    return False


config_now = get_config()

need_reset = (
    "ctrl" not in st.session_state
    or config_changed(st.session_state.get("ctrl_config"), config_now)
)

if need_reset:
    st.session_state.ctrl = SimulationController(**config_now)
    st.session_state.ctrl_config = config_now.copy()
    st.session_state.auto_run = False

if "auto_run" not in st.session_state:
    st.session_state.auto_run = False

ctrl = st.session_state.ctrl
model = ctrl.model

# Sidebar reset
if st.sidebar.button("Reset simulation", use_container_width=True):
    st.session_state.ctrl = SimulationController(**get_config())
    st.session_state.ctrl_config = get_config().copy()
    st.session_state.auto_run = False
    st.rerun()


# ----------------------------------------------------
# Global KPI row
# ----------------------------------------------------
st.divider()

max_temp = model.get_max_temperature()
avg_temp = model.get_average_temperature()
failed_agents = len([a for a in model.thermal_agents if a.status == "failed"])
active_agents = len([a for a in model.thermal_agents if a.status != "failed"])
overloaded_agents = len([a for a in model.thermal_agents if a.task_load > 1])

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Step", model.current_step)
k2.metric("Max Temperature", f"{max_temp:.1f} °C")
k3.metric("Average Temperature", f"{avg_temp:.1f} °C")
k4.metric("Active Agents", active_agents)
k5.metric("Failed Agents", failed_agents)
k6.metric("Recovery Events", model.recovery_events)

system_status_badge(model)

st.divider()

# ----------------------------------------------------
# Controls
# ----------------------------------------------------
st.subheader("Simulation Controls")
control_buttons(ctrl)

st.divider()

# ----------------------------------------------------
# Tabs
# ----------------------------------------------------
tab_dashboard, tab_simulation, tab_simple = st.tabs(
    [
        "Research Dashboard",
        "Visual Simulation",
        "Simplified Demonstration",
    ]
)

with tab_dashboard:
    left, middle, right = st.columns([1.05, 2.0, 1.25])

    with left:
        st.subheader("System Summary")
        st.write(f"**Target temperature:** {model.target_temp:.1f} °C")
        st.write(f"**Unsafe threshold:** {model.unsafe_temp_threshold:.1f} °C")
        st.write(f"**Operational ratio:** {model.get_operational_ratio():.2f}")
        st.write(f"**Overloaded agents:** {overloaded_agents}")
        st.write(f"**Structured events logged:** {len(getattr(model, 'event_log', []))}")

    with middle:
        st.subheader("Thermal Zones")
        for zone_id in range(model.num_agents):
            temp = model.zone_temperatures.get(zone_id, 0.0)
            fan_speed = model.fan_speeds.get(zone_id, 0)
            zone_card(
                zone_id=zone_id,
                temp=temp,
                fan_speed=fan_speed,
                heat_source=model.heat_sources.get(zone_id, 0.0),
                unsafe_threshold=model.unsafe_temp_threshold,
                target_temp=model.target_temp,
            )

            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("Decrease Heat", key=f"heat_minus_{zone_id}", use_container_width=True):
                    current = model.heat_sources.get(zone_id, 5.0)
                    ctrl.set_heat_source(zone_id, max(0.0, current - 1.0))
                    st.rerun()
            with c2:
                st.caption("Thermal disturbance control")
            with c3:
                if st.button("Increase Heat", key=f"heat_plus_{zone_id}", use_container_width=True):
                    current = model.heat_sources.get(zone_id, 5.0)
                    ctrl.set_heat_source(zone_id, current + 1.0)
                    st.rerun()

    with right:
        render_mas_state(model, heartbeat_timeout=model.heartbeat_timeout)

    st.divider()
    st.subheader("Research Charts")
    all_charts(
        ctrl.history,
        num_zones=model.num_agents,
        unsafe_threshold=model.unsafe_temp_threshold,
        target_temp=model.target_temp,
        events=getattr(model, "event_log", []),
    )

with tab_simulation:
    st.subheader("Operational Visualization")
    st.caption(
        "Visual abstraction of zone temperature, fan response, controller ownership, and safety shutdown."
    )
    simulation_animation(
        model,
        unsafe_threshold=model.unsafe_temp_threshold,
        target_temp=model.target_temp,
    )

with tab_simple:
    st.subheader("Simplified Multi-Agent Demonstration")
    st.caption(
        "High-level view of agent availability and task takeover behavior for non-technical audiences."
    )
    simple_agent_view(model, getattr(model, "redistribution_log", []))


# ----------------------------------------------------
# Auto-run loop
# ----------------------------------------------------
if st.session_state.auto_run and not model.system_shutdown:
    for _ in range(num_steps):
        ctrl.run_step()
        if model.system_shutdown:
            break
    time.sleep(0.25)
    st.rerun()
