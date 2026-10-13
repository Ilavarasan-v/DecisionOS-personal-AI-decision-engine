"""
Deterministic scoring logic for DecisionOS.

The scoring engine does not use an LLM.

Its job is purely mathematical:
- Normalize values
- Apply preference weights
- Calculate final weighted scores
"""


from typing import Literal


Direction = Literal[
    "maximize",
    "minimize",
]


def normalize_value(
    value: float,
    minimum: float,
    maximum: float,
    direction: Direction,
) -> float:
    """
    Normalize a value to the range 0-1.

    maximize:
        Higher value = better score.

    minimize:
        Lower value = better score.
    """

    # If every option has the same value,
    # there is no meaningful difference between them.
    if maximum == minimum:
        return 1.0

    if direction == "maximize":

        score = (
            (value - minimum)
            / (maximum - minimum)
        )

    else:

        score = (
            (maximum - value)
            / (maximum - minimum)
        )

    # Keep score strictly within [0, 1].
    return max(
        0.0,
        min(1.0, score),
    )


def calculate_weighted_score(
    normalized_value: float,
    weight: float,
) -> float:
    """
    Apply a preference weight to a normalized score.
    """

    return round(
        normalized_value * weight,
        10,
    )


def calculate_final_score(
    weighted_scores: list[float],
    weights: list[float],
) -> float:
    """
    Calculate the weighted average of criterion scores.
    """

    total_weight = sum(weights)

    if total_weight == 0:
        return 0.0

    return round(
        sum(weighted_scores) / total_weight,
        10,
    )