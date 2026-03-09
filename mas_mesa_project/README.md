# mas_mesa_project

Mesa-based multi-agent scaffold for studying decentralized failure recovery in safety-critical systems.

## Purpose

This project provides a starter architecture to test:

- failure detection through heartbeat monitoring
- decentralized consensus on failed agents
- task redistribution across surviving agents
- safety supervision with a global kill-switch

## Quick start

1. Create a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Run `python run.py`.

The run script exports CSV metrics into `data/results/` for analysis.
Use `notebooks/poster_metrics.ipynb` to generate poster-friendly graphs.

## Status

This is a scaffold with documented placeholders so you can incrementally implement algorithms and experiments.
