"""
Mock AI provider for DecisionOS.

This provider simulates an AI explanation layer without
requiring an external LLM API.
"""

from typing import Any

from backend.app.ai.providers.base import AIProvider


class MockAIProvider(AIProvider):
    """
    Development AI provider used for testing the reasoning layer.

    It does not calculate scores or make decisions.
    It only converts deterministic decision results into
    a human-readable explanation.
    """

    def generate_explanation(
        self,
        decision_context: dict[str, Any],
    ) -> str:
        recommendation = decision_context.get(
            "recommendation",
            "the recommended option",
        )

        score = decision_context.get(
            "recommendation_score",
            0.0,
        )

        preferences = decision_context.get(
            "preferences",
            [],
        )

        ranked_options = decision_context.get(
            "ranked_options",
            [],
        )

        # ---------------------------------------------------------
        # Build preference description
        # ---------------------------------------------------------

        preference_text = ", ".join(
            preference.get("criterion", "unknown")
            for preference in preferences
        )

        # ---------------------------------------------------------
        # Find the recommended option inside ranked options
        # ---------------------------------------------------------

        recommendation_data = None

        for option in ranked_options:
            if option.get("name") == recommendation:
                recommendation_data = option
                break

        # ---------------------------------------------------------
        # Fallback explanation
        # ---------------------------------------------------------

        if recommendation_data is None:
            return (
                f"{recommendation} is recommended based on the "
                f"user's preferences for {preference_text}. "
                f"It received a personalized score of {score:.4f}."
            )

        # ---------------------------------------------------------
        # Extract trade-off information
        # ---------------------------------------------------------

        tradeoffs = recommendation_data.get(
            "tradeoffs",
            {},
        )

        strengths = tradeoffs.get(
            "strengths",
            [],
        )

        weaknesses = tradeoffs.get(
            "weaknesses",
            [],
        )

        # ---------------------------------------------------------
        # Build explanation
        # ---------------------------------------------------------

        explanation = (
            f"{recommendation} is recommended based on the "
            f"user's preferences for {preference_text}. "
            f"It received a personalized score of {score:.4f}."
        )

        if strengths:
            explanation += (
                f" Its main strengths are "
                f"{', '.join(strengths)}."
            )

        if weaknesses:
            explanation += (
                f" Its main trade-off is "
                f"{', '.join(weaknesses)}."
            )

        return explanation