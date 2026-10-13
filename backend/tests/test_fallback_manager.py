from unittest.mock import patch

import pytest

from backend.app.ai.fallback_manager import AIFallbackManager
from backend.app.core.config import settings


def test_provider_order_uses_primary_then_fallbacks(monkeypatch):
    monkeypatch.setattr(
        settings,
        "ai_provider",
        "gemini",
    )

    monkeypatch.setattr(
        settings,
        "ai_fallback_providers",
        "openai,groq",
    )

    manager = AIFallbackManager()

    assert manager.provider_names == [
        "gemini",
        "openai",
        "groq",
    ]


def test_provider_order_removes_duplicates(monkeypatch):
    monkeypatch.setattr(
        settings,
        "ai_provider",
        "gemini",
    )

    monkeypatch.setattr(
        settings,
        "ai_fallback_providers",
        "gemini,openai,openai,groq",
    )

    manager = AIFallbackManager()

    assert manager.provider_names == [
        "gemini",
        "openai",
        "groq",
    ]


def test_manager_returns_first_successful_provider(monkeypatch):
    monkeypatch.setattr(
        settings,
        "ai_provider",
        "gemini",
    )

    monkeypatch.setattr(
        settings,
        "ai_fallback_providers",
        "openai,groq",
    )

    class SuccessfulProvider:
        def generate_explanation(self, decision_context):
            return "Gemini explanation"

    manager = AIFallbackManager()

    with patch.object(
        manager,
        "_create_provider",
        return_value=SuccessfulProvider(),
    ) as create_provider:

        result = manager.generate_explanation(
            {
                "recommendation": "Laptop C",
            }
        )

    assert result == "Gemini explanation"
    create_provider.assert_called_once_with("gemini")


def test_manager_falls_back_when_primary_fails(monkeypatch):
    monkeypatch.setattr(
        settings,
        "ai_provider",
        "gemini",
    )

    monkeypatch.setattr(
        settings,
        "ai_fallback_providers",
        "openai,groq",
    )

    class FailingProvider:
        def generate_explanation(self, decision_context):
            raise RuntimeError("Gemini failed")

    class SuccessfulProvider:
        def generate_explanation(self, decision_context):
            return "OpenAI explanation"

    manager = AIFallbackManager()

    def create_provider(provider_name):
        if provider_name == "gemini":
            return FailingProvider()

        return SuccessfulProvider()

    with patch.object(
        manager,
        "_create_provider",
        side_effect=create_provider,
    ) as create_provider_mock:

        result = manager.generate_explanation(
            {
                "recommendation": "Laptop C",
            }
        )

    assert result == "OpenAI explanation"

    assert create_provider_mock.call_count == 2
    create_provider_mock.assert_any_call("gemini")
    create_provider_mock.assert_any_call("openai")


def test_manager_falls_through_multiple_failures(monkeypatch):
    monkeypatch.setattr(
        settings,
        "ai_provider",
        "gemini",
    )

    monkeypatch.setattr(
        settings,
        "ai_fallback_providers",
        "openai,groq",
    )

    class FailingProvider:
        def __init__(self, name):
            self.name = name

        def generate_explanation(self, decision_context):
            raise RuntimeError(
                f"{self.name} failed"
            )

    manager = AIFallbackManager()

    def create_provider(provider_name):
        return FailingProvider(provider_name)

    with patch.object(
        manager,
        "_create_provider",
        side_effect=create_provider,
    ):

        with pytest.raises(
            RuntimeError,
            match="All configured AI providers failed",
        ) as exc_info:

            manager.generate_explanation(
                {
                    "recommendation": "Laptop C",
                }
            )

    error_message = str(exc_info.value)

    assert "gemini: gemini failed" in error_message
    assert "openai: openai failed" in error_message
    assert "groq: groq failed" in error_message


def test_manager_can_use_only_primary_provider(monkeypatch):
    monkeypatch.setattr(
        settings,
        "ai_provider",
        "gemini",
    )

    monkeypatch.setattr(
        settings,
        "ai_fallback_providers",
        "",
    )

    class SuccessfulProvider:
        def generate_explanation(self, decision_context):
            return "Gemini explanation"

    manager = AIFallbackManager()

    with patch.object(
        manager,
        "_create_provider",
        return_value=SuccessfulProvider(),
    ) as create_provider:

        result = manager.generate_explanation(
            {
                "recommendation": "Laptop C",
            }
        )

    assert result == "Gemini explanation"
    create_provider.assert_called_once_with("gemini")