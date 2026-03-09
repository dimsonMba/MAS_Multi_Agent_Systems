"""Small logging utility for experiment runs."""

from pathlib import Path


def append_log_line(log_path: str, line: str) -> None:
    """Append one line to a log file, creating parent folders if needed."""
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(f"{line}\n")
