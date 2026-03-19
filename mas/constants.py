"""Shared constants for MAS states, roles, and event labels."""

# -----------------------------
# Operational states
# -----------------------------
STATUS_ACTIVE = "active"
STATUS_RECOVERING = "recovering"
STATUS_FAILED = "failed"

# -----------------------------
# Liveness / heartbeat states
# -----------------------------
LIVENESS_HEALTHY = "healthy"
LIVENESS_SUSPECT = "suspect"
LIVENESS_FAILED = "failed"

# -----------------------------
# Roles
# -----------------------------
ROLE_THERMAL = "thermal"
ROLE_SUPERVISOR = "supervisor"
ROLE_RECOVERY = "recovery"

# -----------------------------
# Event types
# -----------------------------
EVENT_AUTO_FAILURE_INJECTED = "auto_failure_injected"
EVENT_RANDOM_FAILURE_INJECTED = "random_failure_injected"
EVENT_MANUAL_FAILURE_INJECTED = "manual_failure_injected"

EVENT_AGENT_SUSPECTED = "agent_suspected"
EVENT_AGENT_FAILED = "agent_failed"
EVENT_HEARTBEAT_FAILURE_DETECTED = "heartbeat_failure_detected"

EVENT_CONSENSUS_COMPLETED = "consensus_completed"
EVENT_ZONE_REASSIGNED = "zone_reassigned"

EVENT_UNSAFE_CONDITION_TRIGGERED = "unsafe_condition_triggered"
EVENT_KILL_SWITCH_TRIGGERED = "kill_switch_triggered"
