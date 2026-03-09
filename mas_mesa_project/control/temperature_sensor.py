"""Temperature sensor abstraction."""

from dataclasses import dataclass


@dataclass
class TemperatureSensor:
    """Simple in-memory sensor model for simulation mode."""

    current_temperature: float = 25.0

    def read(self) -> float:
        """Return current temperature measurement."""
        return self.current_temperature
