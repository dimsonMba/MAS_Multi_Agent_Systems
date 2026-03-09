"""Serial bridge placeholder for Arduino integration."""


class ArduinoBridge:
    """Wrap serial communication details for hardware-in-the-loop tests."""

    def __init__(self, port: str = "/dev/tty.usbmodem", baud_rate: int = 9600) -> None:
        self.port = port
        self.baud_rate = baud_rate

    def connect(self) -> None:
        """Open serial link.

        TODO: Implement with `pyserial` once hardware is available.
        """

    def send_fan_speed(self, speed_percent: int) -> None:
        """Send fan speed command over serial."""
        _ = speed_percent
