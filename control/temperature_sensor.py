"""Temperature sensor abstraction for simulation and future hardware integration."""

from dataclasses import dataclass
import random


@dataclass
class TemperatureSensor:
    """
    Simple sensor model.

    Supports optional Gaussian-like measurement noise and calibration offset
    to better approximate physical sensing conditions.
    """

    current_temperature: float = 25.0
    noise_std: float = 0.0
    calibration_offset: float = 0.0

    def read(self) -> float:
        """Return current temperature measurement."""
        noise = random.gauss(0.0, self.noise_std) if self.noise_std > 0 else 0.0
        return self.current_temperature + self.calibration_offset + noise
