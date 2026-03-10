# MAS Mesa Project – Decentralized Failure Recovery

Mesa-based multi-agent scaffold for studying **decentralized failure detection, task redistribution, and safety supervision** in safety‑critical systems (e.g., thermal management with fans and sensors, later Arduino integration).

---

## 1. Project Goal

Build a Mesa-based Multi‑Agent System (MAS) simulation that lets you:

- **Inject failures** into agents or communication links.
- **Detect failures** using heartbeat signals and timeouts.
- **Reach decentralized agreement** on which agents are failed.
- **Redistribute tasks** across surviving agents.
- **Enforce safety** using a global kill‑switch when temperatures exceed safe thresholds.
- Keep a **clean separation** between simulation logic and real‑world control logic (Arduino / fan controller), so you can later attach hardware without rewriting the MAS core.

---

## 2. Recommended Folder Structure

The scaffold is organized so that simulation, control logic, hardware, and documentation are clearly separated.

```text
mas_mesa_project/
│
├── README.md
├── requirements.txt
├── run.py
├── config.py
├── .gitignore
│
├── data/
│   ├── logs/
│   └── results/
│
├── docs/
│   ├── architecture_notes.md
│   └── experiment_plan.md
│
├── mas/
│   ├── __init__.py
│   ├── model.py
│   ├── scheduler.py
│   ├── environment.py
│   ├── metrics.py
│   ├── constants.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── thermal_agent.py
│   │   ├── supervisor_agent.py
│   │   └── recovery_agent.py
│   │
│   ├── protocols/
│   │   ├── __init__.py
│   │   ├── heartbeat.py
│   │   ├── consensus.py
│   │   ├── redistribution.py
│   │   └── kill_switch.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       ├── helpers.py
│       └── plotting.py
│
├── control/
│   ├── __init__.py
│   ├── control_interface.py
│   ├── fan_controller.py
│   ├── temperature_sensor.py
│   ├── thermal_model.py
│   └── arduino_bridge.py
│
├── hardware/
│   ├── arduino/
│   │   └── fan_control.ino
│   └── wiring_notes.md
│
└── tests/
    ├── __init__.py
    ├── test_heartbeat.py
    ├── test_consensus.py
    ├── test_killswitch.py
    └── test_thermal_agent.py
```

> If some of these files do not exist yet in your local checkout, treat this as the **target structure** you are working toward while you implement the MAS.

---

## 3. What Each Part Does

### `mas/` – Core Mesa simulation

- `model.py`: main Mesa model definition (agents, schedule, environment).
- `environment.py`: temperature zones, heat sources, shared environment state.
- `scheduler.py`: custom activation order (e.g., by role, round‑robin, or priority).
- `metrics.py`: data collection for resilience, recovery time, and safety violations.
- `constants.py`: shared constants for the MAS (roles, states, message types, etc.).

**Agents (`mas/agents/`):**

- `base_agent.py`: common behavior and utilities for all agents.
- `thermal_agent.py`: local temperature monitoring and actuation requests.
- `supervisor_agent.py`: high‑level monitoring, global policy, and kill‑switch triggers.
- `recovery_agent.py`: coordination of task redistribution and recovery actions.

**Protocols (`mas/protocols/`):**

- `heartbeat.py`: periodic liveness checks; tracks missed heartbeats per agent.
- `consensus.py`: decentralized agreement on failed agents or unsafe conditions.
- `redistribution.py`: logic for reassigning tasks after failures.
- `kill_switch.py`: centralized or distributed kill‑switch policy for safety shutdown.

**Utilities (`mas/utils/`):**

- `logger.py`: structured logging of events and metrics.
- `helpers.py`: common helper functions (ID generation, message helpers, etc.).
- `plotting.py`: helper functions for visualizing results / metrics.

### `control/` – Real‑world control abstraction

Separates real fan/sensor logic from the Mesa simulation so you can swap in either pure simulation or hardware‑in‑the‑loop.

- `control_interface.py`: boundary between MAS world and control world.
- `fan_controller.py`: mapping from MAS commands to fan RPM or duty cycle.
- `temperature_sensor.py`: abstract sensor interface (real or simulated).
- `thermal_model.py`: simulation of temperature dynamics for virtual experiments.
- `arduino_bridge.py`: serial communication layer for an Arduino‑based prototype.

### `hardware/arduino/`

- `fan_control.ino`: Arduino firmware for driving fans based on MAS commands.
- `wiring_notes.md`: documentation of wiring, pin mapping, and safety notes.

### `data/` and `docs/`

- `data/logs/`: raw event logs (e.g., failures, recoveries, temperature traces).
- `data/results/`: CSV files and processed metrics for analysis.
- `docs/architecture_notes.md`: higher‑level design and rationale.
- `docs/experiment_plan.md`: scenarios, parameters, and hypotheses for experiments.

### `tests/`

Unit tests for protocol and agent behavior, e.g.:

- `test_heartbeat.py`: missed heartbeat and timeout behavior.
- `test_consensus.py`: convergence and disagreement cases.
- `test_killswitch.py`: correct triggering / non‑triggering of the kill‑switch.
- `test_thermal_agent.py`: local sensing and control logic.

---

## 4. Quick Start

1. **Create a virtual environment** (example using `venv`):

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
   ```

2. **Install dependencies** from `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the simulation**:

   ```bash
   python run.py
   ```

4. **Inspect results**:

   - CSV metrics are exported to `data/results/` for further analysis.
   - Logs (if enabled) are written to `data/logs/`.

5. (Optional) **Generate plots / poster figures**:

   - Use `notebooks/poster_metrics.ipynb` (or similar notebooks) to build graphs for reports, posters, or papers.

6. **Run the simulation dashboard** (interactive UI):

   ```bash
   pip install -r requirements.txt   # includes streamlit, plotly
   streamlit run UI/app.py
   ```

   The dashboard provides:
   - **Left**: System controls (Start, Pause, Step, Inject Failure, Trigger Unsafe, Reset)
   - **Middle**: Thermal zones (temp, fan speed, heat source) with color-coded temperature
   - **Right**: MAS state (agent status, heartbeat, redistribution log, kill-switch)
   - **Bottom**: Charts (temperature, fan speed, failed agents, recovery events)
   - **Sidebar**: Full configuration (agents, temps, thresholds) and manual overrides

---

## 5. Configuration

High‑level defaults live in `config.py`, for example:

- `DEFAULT_AGENT_COUNT`
- `DEFAULT_GRID_WIDTH`, `DEFAULT_GRID_HEIGHT`
- `DEFAULT_STEPS`
- `FAILURE_PROBABILITY`
- `HEARTBEAT_TIMEOUT_STEPS`
- `CRITICAL_TEMPERATURE`, `KILL_SWITCH_ENABLED`

Adjust these values to match specific experiment scenarios (e.g., more agents, higher failure rates, more aggressive safety thresholds).

---

## 6. Project Status

This repository is currently a **scaffold**: many components are intentionally minimal or placeholder so that you can incrementally implement:

- failure‑detection protocols,
- decentralized recovery strategies,
- safety policies and kill‑switch behavior,
- and experiment pipelines for your research on **enhancing resilience and safety in MAS**.

As you implement pieces, update this README to reflect what is fully implemented vs. still planned.
