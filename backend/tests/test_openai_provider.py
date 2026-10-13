
from unittest.mock import patch

import pytest

from backend.app.ai.providers.openai import OpenAIProvider


def test_openai_provider_requires_api_key():
    with patch(
        "backend.app.ai.providers.openai.settings.openai_api_key",
        None,
    ):
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            OpenAIProvider()


def test_openai_prompt_contains_decision_context():
    prompt = OpenAIProvider._build_prompt(
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


def test_openai_provider_generates_explanation():
    expected_explanation = (
        "Laptop C fits the user's preferences "
        "because it provides strong value."
    )

    class MockMessage:
        content = expected_explanation

    class MockChoice:
        message = MockMessage()

    class MockResponse:
        choices = [MockChoice()]

    class MockCompletions:
        def create(self, model, messages, temperature):
            assert model == "gpt-test-model"
            assert temperature == 0.2

            # Verify that the decision context reaches the model.
            user_messages = [
                message["content"]
                for message in messages
                if message["role"] == "user"
            ]

            assert user_messages
            assert "Laptop C" in user_messages[0]

            return MockResponse()

    class MockChat:
        def __init__(self):
            self.completions = MockCompletions()

    class MockClient:
        def __init__(self):
            self.chat = MockChat()

    with patch(
        "backend.app.ai.providers.openai.settings.openai_api_key",
        "test-key",
    ), patch(
        "backend.app.ai.providers.openai.settings.openai_model",
        "gpt-test-model",
    ), patch(
        "backend.app.ai.providers.openai.OpenAI",
        return_value=MockClient(),
    ):
        provider = OpenAIProvider()

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

    assert explanation == expected_explanation
