from unittest.mock import patch

from backend.app.ai.fallback_manager import AIFallbackManager
from backend.app.ai.reasoning_service import (
    build_reasoning_context,
    generate_decision_explanation,
)


def test_build_reasoning_context():
    recommendation = {
        "name": "Laptop C",
        "score": 0.625,
    }

    ranked_options = [
        {
            "name": "Laptop C",
            "score": 0.625,
            "rank": 1,
        },
        {
            "name": "Laptop A",
            "score": 0.5486,
            "rank": 2,
        },
    ]

    preferences = [
        {
            "criterion": "price",
            "weight": 0.80,
            "direction": "minimize",
        },
        {
            "criterion": "performance",
            "weight": 0.90,
            "direction": "maximize",
        },
        {
            "criterion": "battery",
            "weight": 0.70,
            "direction": "maximize",
        },
    ]

    context = build_reasoning_context(
        recommendation=recommendation,
        ranked_options=ranked_options,
        preferences=preferences,
    )

    assert context["recommendation"] == "Laptop C"
    assert context["recommendation_score"] == 0.625
    assert len(context["ranked_options"]) == 2
    assert len(context["preferences"]) == 3
    assert context["preferences"][0]["criterion"] == "price"


def test_generate_decision_explanation():
    recommendation = {
        "name": "Laptop C",
        "score": 0.625,
    }

    ranked_options = [
        {
            "name": "Laptop C",
            "score": 0.625,
            "rank": 1,
        },
    ]

    preferences = [
        {
            "criterion": "price",
            "weight": 0.80,
            "direction": "minimize",
        },
        {
            "criterion": "performance",
            "weight": 0.90,
            "direction": "maximize",
        },
    ]

    class MockFallbackManager:
        def generate_explanation(self, decision_context):
            assert decision_context["recommendation"] == "Laptop C"
            assert decision_context["recommendation_score"] == 0.625
            assert len(decision_context["preferences"]) == 2

            return (
                "Laptop C is recommended because it fits "
                "the user's preferences."
            )

    manager = MockFallbackManager()

    explanation = generate_decision_explanation(
        recommendation=recommendation,
        ranked_options=ranked_options,
        preferences=preferences,
        fallback_manager=manager,
    )

    assert "Laptop C" in explanation
    assert "user's preferences" in explanation


def test_generate_decision_explanation_includes_tradeoffs():
    recommendation = {
        "name": "Laptop C",
        "score": 0.625,
    }

    ranked_options = [
        {
            "name": "Laptop C",
            "score": 0.625,
            "rank": 1,
            "tradeoffs": {
                "strengths": [
                    "price",
                    "battery",
                ],
                "weaknesses": [
                    "performance",
                ],
            },
        }
    ]

    preferences = [
        {
            "criterion": "price",
            "weight": 0.80,
            "direction": "minimize",
        },
        {
            "criterion": "performance",
            "weight": 0.90,
            "direction": "maximize",
        },
        {
            "criterion": "battery",
            "weight": 0.70,
            "direction": "maximize",
        },
    ]

    class MockFallbackManager:
        def generate_explanation(self, decision_context):
            option = decision_context["ranked_options"][0]
            tradeoffs = option["tradeoffs"]

            assert "price" in tradeoffs["strengths"]
            assert "battery" in tradeoffs["strengths"]
            assert "performance" in tradeoffs["weaknesses"]

            return (
                "Laptop C is recommended. "
                "Its strengths are price and battery, "
                "while performance is its main trade-off."
            )

    manager = MockFallbackManager()

    explanation = generate_decision_explanation(
        recommendation=recommendation,
        ranked_options=ranked_options,
        preferences=preferences,
        fallback_manager=manager,
    )

    assert "Laptop C" in explanation
    assert "price" in explanation
    assert "battery" in explanation
    assert "performance" in explanation


def test_reasoning_service_creates_fallback_manager_when_not_supplied():
    recommendation = {
        "name": "Laptop C",
        "score": 0.625,
    }

    ranked_options = [
        {
            "name": "Laptop C",
            "score": 0.625,
            "rank": 1,
        },
    ]

    preferences = [
        {
            "criterion": "price",
            "weight": 0.80,
            "direction": "minimize",
        },
    ]

    with patch(
        "backend.app.ai.reasoning_service.AIFallbackManager"
    ) as manager_class:

        manager = manager_class.return_value

        manager.generate_explanation.return_value = (
            "Laptop C is recommended."
        )

        explanation = generate_decision_explanation(
            recommendation=recommendation,
            ranked_options=ranked_options,
            preferences=preferences,
        )

    manager_class.assert_called_once()

    manager.generate_explanation.assert_called_once()

    assert explanation == "Laptop C is recommended."