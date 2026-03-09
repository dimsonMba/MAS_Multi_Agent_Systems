"""Plotting helpers for resilience metrics."""

import matplotlib.pyplot as plt


def plot_alive_vs_failed(steps: list[int], alive: list[int], failed: list[int]) -> None:
    """Quick diagnostic chart for simulation health over time."""
    plt.figure(figsize=(8, 4))
    plt.plot(steps, alive, label="alive_agents")
    plt.plot(steps, failed, label="failed_agents")
    plt.xlabel("step")
    plt.ylabel("agents")
    plt.title("Resilience Trend")
    plt.legend()
    plt.tight_layout()
    plt.show()
