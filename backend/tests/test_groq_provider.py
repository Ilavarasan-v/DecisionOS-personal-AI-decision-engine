from unittest.mock import patch

import pytest

from backend.app.ai.providers.groq import GroqAIProvider


def test_groq_provider_requires_api_key():
    with patch(
        "backend.app.ai.providers.groq.settings.groq_api_key",
        None,
    ):
        with pytest.raises(ValueError, match="GROQ_API_KEY"):
            GroqAIProvider()


def test_groq_prompt_contains_decision_context():
    prompt = GroqAIProvider._build_prompt(
        recommendation="Laptop C",
        recommendation_score=0.625,
        preferences=[
            {
                "criterion": "price",
                "weight": 0.8,
                "direction": "minimize",
            },
            {
                "criterion": "performance",
                "weight": 0.9,
                "direction": "maximize",
            },
        ],
        ranked_options=[
            {
                "name": "Laptop C",
                "score": 0.625,
                "rank": 1,
                "tradeoffs": {
                    "strengths": ["price"],
                    "weaknesses": ["performance"],
                },
            },
        ],
    )

    assert "Laptop C" in prompt
    assert "0.6250" in prompt
    assert "price" in prompt
    assert "performance" in prompt
    assert "minimize" in prompt
    assert "maximize" in prompt


def test_groq_provider_generates_explanation():
    class MockMessage:
        content = (
            "Laptop C fits the user's preferences "
            "because it provides strong value."
        )

    class MockChoice:
        message = MockMessage()

    class MockResponse:
        choices = [MockChoice()]

    class MockCompletions:
        def create(self, model, messages, temperature):
            assert model == "groq-test-model"
            assert temperature == 0.2
            assert any(
                "Laptop C" in message["content"]
                for message in messages
            )
            return MockResponse()

    class MockChat:
        completions = MockCompletions()

    class MockClient:
        chat = MockChat()

    with patch(
        "backend.app.ai.providers.groq.settings.groq_api_key",
        "test-key",
    ), patch(
        "backend.app.ai.providers.groq.settings.groq_model",
        "groq-test-model",
    ), patch(
        "backend.app.ai.providers.groq.Groq",
        return_value=MockClient(),
    ):
        provider = GroqAIProvider()

        explanation = provider.generate_explanation(
            {
                "recommendation": "Laptop C",
                "recommendation_score": 0.625,
                "preferences": [
                    {
                        "criterion": "price",
                        "weight": 0.8,
                        "direction": "minimize",
                    }
                ],
                "ranked_options": [
                    {
                        "name": "Laptop C",
                        "score": 0.625,
                        "rank": 1,
                        "tradeoffs": {
                            "strengths": ["price"],
                            "weaknesses": [],
                        },
                    }
                ],
            }
        )

    assert explanation == (
        "Laptop C fits the user's preferences "
        "because it provides strong value."
    )