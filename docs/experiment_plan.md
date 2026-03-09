# Experiment Plan

## Goal

Evaluate resilience and safety of decentralized failure recovery in MAS.

## Baseline Experiments

1. No failure injection.
2. Random single-agent failures.
3. Clustered failures (adjacent agents fail close in time).

## Metrics

- failure detection latency
- recovery time to stable load distribution
- count of safety threshold violations
- percentage of tasks successfully reassigned

## Next Steps

Implement reproducible seeds and batch runs with result export.
