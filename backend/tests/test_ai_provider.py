from backend.app.ai.providers import MockAIProvider


def test_mock_ai_provider_generates_explanation():
    provider = MockAIProvider()

    context = {
        "recommendation": "Laptop C",
        "recommendation_score": 0.625,
    }

    explanation = provider.generate_explanation(context)

    assert "Laptop C" in explanation
    assert "0.6250" in explanation
    assert "recommended" in explanation