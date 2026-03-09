"""Metrics helpers for resilience and safety analysis."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class MetricsSnapshot:
    """Single-step metrics snapshot for later logging/export."""

    step: int
    alive_agents: int
    failed_agents: int
    hazard_flag: bool
    total_failure_events: int
    operational_ratio: float

    def to_dict(self) -> dict:
        """Return dict form for CSV/JSON pipelines."""
        return asdict(self)


def export_metrics_to_csv(metrics_history: list[MetricsSnapshot], output_path: str) -> str:
    """Export collected metrics snapshots to CSV.

    Returns the absolute path to the generated CSV file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    rows = [snapshot.to_dict() for snapshot in metrics_history]
    if not rows:
        # Keep schema explicit even when no rows exist yet.
        fieldnames = [
            "step",
            "alive_agents",
            "failed_agents",
            "hazard_flag",
            "total_failure_events",
            "operational_ratio",
        ]
    else:
        fieldnames = list(rows[0].keys())

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return str(path.resolve())
