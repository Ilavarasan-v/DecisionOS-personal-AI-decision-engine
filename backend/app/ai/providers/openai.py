"""
OpenAI AI provider for DecisionOS.

Uses the OpenAI SDK to generate natural-language
explanations for deterministic decisions.
"""

from typing import Any

from openai import OpenAI

from backend.app.ai.providers.base import AIProvider
from backend.app.core.config import settings


class OpenAIProvider(AIProvider):
    """
    OpenAI implementation of the DecisionOS AI provider.

    The provider does not calculate scores or select
    recommendations. It only explains the results
    produced by the deterministic decision engine.
    """

    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=settings.openai_api_key
        )

        self.model = settings.openai_model

    def generate_explanation(
        self,
        decision_context: dict[str, Any],
    ) -> str:
        """
        Generate an explanation for the deterministic
        decision result.
        """

        recommendation = decision_context.get(
            "recommendation",
            "the recommended option",
        )

        recommendation_score = decision_context.get(
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

        prompt = self._build_prompt(
            recommendation=recommendation,
            recommendation_score=recommendation_score,
            preferences=preferences,
            ranked_options=ranked_options,
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are the explanation layer of "
                        "DecisionOS. Explain deterministic "
                        "decision results without changing "
                        "the ranking or recommendation."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
        )

        if not response.choices:
            raise RuntimeError(
                "OpenAI returned no choices."
            )

        explanation = response.choices[0].message.content

        if not explanation:
            raise RuntimeError(
                "OpenAI returned an empty response."
            )

        return explanation.strip()

    @staticmethod
    def _build_prompt(
        recommendation: str,
        recommendation_score: float,
        preferences: list[dict[str, Any]],
        ranked_options: list[dict[str, Any]],
    ) -> str:
        """
        Build the explanation prompt from deterministic
        DecisionOS evaluation results.
        """

        preference_lines = []

        for preference in preferences:
            criterion = preference.get(
                "criterion",
                "unknown",
            )

            weight = preference.get(
                "weight",
                0.0,
            )

            direction = preference.get(
                "direction",
                "maximize",
            )

            preference_lines.append(
                f"- {criterion}: "
                f"weight={weight}, "
                f"direction={direction}"
            )

        option_lines = []

        for option in ranked_options:
            name = option.get(
                "name",
                "unknown",
            )

            score = option.get(
                "score",
                0.0,
            )

            rank = option.get(
                "rank",
                "unknown",
            )

            tradeoffs = option.get(
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

            option_lines.append(
                f"- {name}: "
                f"rank={rank}, "
                f"score={score:.4f}, "
                f"strengths={strengths}, "
                f"weaknesses={weaknesses}"
            )

        preferences_text = (
            "\n".join(preference_lines)
            if preference_lines
            else "No preferences provided."
        )

        options_text = (
            "\n".join(option_lines)
            if option_lines
            else "No ranked options provided."
        )

        return f"""
You are the explanation layer of DecisionOS,
a personal AI decision engine.

Your job is to explain a decision that has ALREADY
been calculated by a deterministic scoring engine.

IMPORTANT:
- Do not recalculate the scores.
- Do not change the ranking.
- Do not select a different recommendation.
- Do not invent user preferences.
- Use only the information provided below.
- Clearly mention important trade-offs.
- Keep the explanation concise and understandable.
- Explain why the recommendation fits the user's preferences.

Recommended option:
{recommendation}

Recommendation score:
{recommendation_score:.4f}

User preferences:
{preferences_text}

Ranked options:
{options_text}

Write a concise explanation containing:
1. Why the recommended option fits the user's preferences.
2. Its strongest advantages.
3. Its most important trade-off or weakness.
4. A brief comparison with the alternatives when useful.

Return only the explanation text.
""".strip()