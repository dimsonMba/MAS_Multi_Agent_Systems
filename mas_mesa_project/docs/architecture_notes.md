# Architecture Notes

## Intent

The system models a decentralized MAS where each agent can:

- monitor neighbors through heartbeat messages
- vote on suspected failures
- participate in task reassignment

## Layers

- `mas/`: simulation behavior and resilience protocols
- `control/`: abstract control systems (fans, sensors, thermal dynamics)
- `hardware/`: deployment-facing firmware placeholders

## Extension Points

- Add communication topology logic in `mas/protocols/consensus.py`
- Add richer fault models in `mas/agents/thermal_agent.py`
- Add real serial control in `control/arduino_bridge.py`
