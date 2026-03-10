"""
Arduino bridge: serial communication for hardware fan control.

Sends fan commands (FAN,fan_id,speed) and reads sensor data.
When port is None, runs in simulation-only mode (no serial connection).
"""


class ArduinoBridge:
    """
    Serial bridge to Arduino for fan control and sensor reading.

    If port is None, connect() and send/read are no-ops (simulation mode).
    """

    def __init__(self, port: str | None = None, baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None

    def connect(self) -> None:
        """Open serial connection if port is configured."""
        if self.port is None:
            return
        import serial
        self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)

    def send_fan_command(self, fan_id: int, speed: int) -> None:
        """
        Send a fan command: FAN,fan_id,speed (no spaces for parsing).

        Args:
            fan_id: Fan index (0–2 for typical hardware).
            speed: PWM value (0–255).
        """
        if self.serial_conn is None:
            return
        command = f"FAN,{fan_id},{speed}\n"
        self.serial_conn.write(command.encode())

    def read_sensor_data(self) -> str | None:
        """Read one line from serial; returns None if not connected."""
        if self.serial_conn is None:
            return None
        return self.serial_conn.readline().decode().strip()
