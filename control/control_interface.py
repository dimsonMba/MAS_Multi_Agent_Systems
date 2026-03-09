"""Abstract control interface to unify simulation and hardware modes."""

from abc import ABC, abstractmethod


class ControlInterface(ABC):
    """Defines operations expected from any control backend."""

    @abstractmethod
    def read_temperature(self) -> float:
        """Return current measured temperature."""

    @abstractmethod
    def set_fan_speed(self, speed_percent: int) -> None:
        """Set fan actuation level as percentage."""
