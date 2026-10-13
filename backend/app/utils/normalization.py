"""
Shared numeric normalization helpers used by the scoring and preference
services.
"""

from typing import Dict


def normalize_weights(raw_weights: Dict[str, float]) -> Dict[str, float]:
    """
    Scale a dict of category -> raw weight so the values sum to 1.0.
    Returns an empty dict unchanged, and handles an all-zero input
    by falling back to equal weighting.
    """
    if not raw_weights:
        return {}

    total = sum(raw_weights.values())
    if total <= 0:
        equal_share = 1.0 / len(raw_weights)
        return {category: equal_share for category in raw_weights}

    return {category: round(weight / total, 4) for category, weight in raw_weights.items()}


def min_max_normalize(value: float, min_value: float, max_value: float) -> float:
    """Scale `value` into the 0.0-1.0 range given the observed min/max bounds."""
    if max_value == min_value:
        return 0.5  # no variance in the data; treat as neutral
    return round((value - min_value) / (max_value - min_value), 4)
