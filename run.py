"""
Entry point for running the resilient thermal MAS simulation.

Creates a ThermalMASModel, runs it for a fixed number of steps,
exports metrics to CSV, and prints the last few rows.
"""

from pathlib import Path

from mas.model import ThermalMASModel


def main() -> None:
    model = ThermalMASModel(
        num_agents=3,
        width=5,
        height=5,
        initial_temps=[45.0, 50.0, 55.0],
        failure_step=20,
        unsafe_temp_threshold=80.0,
    )

    for _ in range(50):
        model.step()

    df = model.datacollector.get_model_vars_dataframe()

    # Export to CSV
    results_dir = Path(__file__).parent / "data" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "simulation_metrics.csv"
    df.to_csv(csv_path, index=False)
    print(f"Metrics saved to {csv_path}")

    print(df.tail())


if __name__ == "__main__":
    main()
