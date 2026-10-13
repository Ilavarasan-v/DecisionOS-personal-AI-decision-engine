from unittest.mock import patch

import pytest

from backend.app.ai.providers.gemini import GeminiAIProvider


def test_gemini_provider_requires_api_key():
    with patch(
        "backend.app.ai.providers.gemini.settings.gemini_api_key",
        None,
    ):
        with pytest.raises(ValueError, match="GEMINI_API_KEY"):
            GeminiAIProvider()


def test_gemini_prompt_contains_decision_context():
    prompt = GeminiAIProvider._build_prompt(
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


def test_gemini_provider_generates_explanation():
    class MockResponse:
        text = "Laptop C fits the user's preferences because it provides strong value."

    class MockModels:
        def generate_content(self, model, contents):
            assert model == "gemini-test-model"
            assert "Laptop C" in contents
            return MockResponse()

    class MockClient:
        def __init__(self):
            self.models = MockModels()

    with patch(
        "backend.app.ai.providers.gemini.settings.gemini_api_key",
        "test-key",
    ), patch(
        "backend.app.ai.providers.gemini.settings.gemini_model",
        "gemini-test-model",
    ), patch(
        "backend.app.ai.providers.gemini.genai.Client",
        return_value=MockClient(),
    ):
        provider = GeminiAIProvider()

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
        "Laptop C fits the user's preferences because it provides strong value."
    )