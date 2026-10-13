"""
Ranking logic for DecisionOS.

This module evaluates multiple decision options and ranks them
from highest personalized score to lowest.
"""

from typing import Dict, List

from backend.app.services.decision_service import evaluate_option


def rank_options(
    options: List[Dict],
    preferences: Dict[str, dict],
) -> list[dict]:
    """
    Evaluate and rank multiple options against user preferences.

    Parameters
    ----------
    options:
        List of decision options.

        Example:
        [
            {
                "name": "Laptop A",
                "price": 85000,
                "performance": 8.5,
                "battery": 9,
            },
            ...
        ]

    preferences:
        User preference configuration.

    Returns
    -------
    list[dict]
        Options ranked from highest score to lowest score.
    """

    ranked_options = []

    for option in options:
        # Keep the option name separate from numerical attributes.
        option_name = option.get("name", "Unnamed Option")

        attributes = {
            key: value
            for key, value in option.items()
            if key != "name"
            and isinstance(value, (int, float))
        }

        evaluation = evaluate_option(
            option_attributes=attributes,
            preferences=preferences,
        )

        ranked_options.append(
            {
                "name": option_name,
                "final_score": evaluation["final_score"],
                "criteria": evaluation["criteria"],
            }
        )

    # Highest score first.
    ranked_options.sort(
        key=lambda option: option["final_score"],
        reverse=True,
    )

    # Add ranking position.
    for position, option in enumerate(ranked_options, start=1):
        option["rank"] = position

    return ranked_options