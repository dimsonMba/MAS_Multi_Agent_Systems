"""Shared environment state for thermal and safety simulation."""

from dataclasses import dataclass


@dataclass
class EnvironmentState:
    """Minimal environment snapshot used by agents each step."""

    ambient_temperature: float = 25.0
    system_load: float = 0.50
    hazard_flag: bool = False
