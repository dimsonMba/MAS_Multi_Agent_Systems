"""Shared environment state for plant-level simulation."""

from dataclasses import dataclass


@dataclass
class EnvironmentState:
    """
    Environment-level state affecting all thermal zones.

    Attributes:
        ambient_temperature: Background room/plant temperature.
        system_load: Global load factor that can scale heat generation.
        hazard_flag: True when system is in unsafe or emergency condition.
    """

    ambient_temperature: float = 25.0
    system_load: float = 0.50
    hazard_flag: bool = False
