"""General helper functions used across modules."""


def clamp(value: float, low: float, high: float) -> float:
    """Clamp numeric value within a closed interval."""
    return max(low, min(value, high))
