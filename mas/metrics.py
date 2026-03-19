"""Metrics helpers for resilience and safety analysis."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class MetricsSnapshot:
    """Single-step metrics snapshot for resilience experiments."""

    step: int
    active_agents: int
    suspected_agents: int
    failed_agents: int
    overloaded_agents: int
    hazard_flag: bool
    total_failure_events: int
    recovery_events: int
    operational_ratio: float
    max_temperature: float
    average_temperature: float
    system_shutdown: bool

    def to_dict(self) -> dict:
        return asdict(self)


def export_metrics_to_csv(metrics_history: list[MetricsSnapshot], output_path: str) -> str:
    """Export collected metrics snapshots to CSV and return absolute path."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    rows = [snapshot.to_dict() for snapshot in metrics_history]

    if rows:
        fieldnames = list(rows[0].keys())
    else:
        fieldnames = [
            "step",
            "active_agents",
            "suspected_agents",
            "failed_agents",
            "overloaded_agents",
            "hazard_flag",
            "total_failure_events",
            "recovery_events",
            "operational_ratio",
            "max_temperature",
            "average_temperature",
            "system_shutdown",
        ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return str(path.resolve())
