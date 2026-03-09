# Mesa MAS Project Scaffold

## Project Goal

Build a **Mesa-based Multi-Agent System (MAS)** simulation for decentralized failure detection, task redistribution, and safety supervision, while also keeping a clean path for later integration with **Arduino / fan-control prototype logic**.

---

## Recommended Folder Structure

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

---

## What Each Part Does

### `mas/`

Core Mesa simulation.

* `model.py`: the main Mesa model
* `environment.py`: temperature zones, heat sources, shared environment state
* `scheduler.py`: custom activation order if needed
* `metrics.py`: data collection, resilience, recovery time, safety violations
* `agents/`: all agent classes
* `protocols/`: heartbeat, failure recovery, consensus, kill-switch logic

### `control/`

Separates real-world fan/sensor logic from simulation logic.

* `fan_controller.py`: fan speed logic
* `temperature_sensor.py`: abstract sensor interface
* `thermal_model.py`: simulated temperature dynamics
* `arduino_bridge.py`: later serial communication with Arduino

### `hardware/arduino/`

Actual Arduino firmware for fans/sensors.

---

## `requirements.txt`

```txt
mesa
numpy
pandas
matplotlib
pyserial
pytest
networkx
```

Optional later:

```txt
scipy
seaborn
```

