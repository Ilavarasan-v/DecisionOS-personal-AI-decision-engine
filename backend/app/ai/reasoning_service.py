"""
DecisionOS AI reasoning service.

Responsibilities:
- Build the context passed to an AI provider
- Include recommendation details
- Include user preference information
- Include ranked option trade-offs
- Generate the final decision explanation
- Support automatic AI provider fallback
"""

from typing import Any

from backend.app.ai.fallback_manager import AIFallbackManager


def build_reasoning_context(
    recommendation: dict[str, Any],
    ranked_options: list[dict[str, Any]],
    preferences: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Build the structured context used by the AI reasoning layer.
    """

    return {
        "recommendation": recommendation["name"],
        "recommendation_score": recommendation["score"],
        "preferences": preferences,
        "ranked_options": ranked_options,
    }


def generate_decision_explanation(
    recommendation: dict[str, Any],
    ranked_options: list[dict[str, Any]],
    preferences: list[dict[str, Any]],
    fallback_manager: AIFallbackManager | None = None,
) -> str:
    """
    Generate a natural-language explanation for a deterministic
    decision result.

    The deterministic engine has already calculated the ranking.
    The AI layer only explains the result.

    If a fallback manager is not supplied, a new one is created.
    """

    context = build_reasoning_context(
        recommendation=recommendation,
        ranked_options=ranked_options,
        preferences=preferences,
    )

    manager = fallback_manager or AIFallbackManager()

    return manager.generate_explanation(
        decision_context=context
    )