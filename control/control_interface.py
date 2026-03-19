"""Abstract control interface for simulation and hardware backends."""

from abc import ABC, abstractmethod


class ControlInterface(ABC):
    """
    Unified interface for plant interaction.

    This abstraction allows the MAS logic to run against:
    - pure software simulation
    - hardware testbed (Arduino / ESP32 / Raspberry Pi)
    - hybrid digital twin environments
    """

    @abstractmethod
    def read_temperature(self, zone_id: int) -> float:
        """Return the measured temperature for a zone."""

    @abstractmethod
    def set_fan_speed(self, zone_id: int, speed_percent: int) -> None:
        """Set fan actuation level (0-100%) for a zone."""

    @abstractmethod
    def shutdown(self) -> None:
        """Place the backend into a safe shutdown state."""
