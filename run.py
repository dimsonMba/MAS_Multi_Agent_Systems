"""Entrypoint for running a small scaffold simulation."""

from datetime import datetime
from pathlib import Path

from config import DEFAULT_AGENT_COUNT, DEFAULT_GRID_HEIGHT, DEFAULT_GRID_WIDTH, DEFAULT_STEPS
from mas.metrics import export_metrics_to_csv
from mas.model import ResilientMASModel


def main() -> None:
    """Run the model for a fixed number of steps."""
    model = ResilientMASModel(
        width=DEFAULT_GRID_WIDTH,
        height=DEFAULT_GRID_HEIGHT,
        n_agents=DEFAULT_AGENT_COUNT,
    )

    for _ in range(DEFAULT_STEPS):
        model.step()

    # Export step-by-step metrics for notebook analysis and poster visuals.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path("data/results") / f"metrics_{timestamp}.csv"
    csv_path = export_metrics_to_csv(model.metrics_history, str(output_file))

    print("Simulation complete.")
    print(f"Steps executed: {model.current_step}")
    print(f"Detected failures: {model.failure_events}")
    print(f"Metrics exported to: {csv_path}")


if __name__ == "__main__":
    main()
