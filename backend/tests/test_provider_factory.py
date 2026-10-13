import pytest

from backend.app.ai.providers.factory import get_ai_provider
from backend.app.ai.providers.gemini import GeminiAIProvider
from backend.app.ai.providers.groq import GroqAIProvider
from backend.app.ai.providers.mock import MockAIProvider
from backend.app.ai.providers.openai import OpenAIProvider
from backend.app.core.config import settings


def test_factory_returns_mock_provider():
    original_provider = settings.ai_provider

    try:
        settings.ai_provider = "mock"

        provider = get_ai_provider()

        assert isinstance(provider, MockAIProvider)

    finally:
        settings.ai_provider = original_provider


def test_factory_returns_gemini_provider(monkeypatch):
    monkeypatch.setattr(
        settings,
        "ai_provider",
        "gemini",
    )

    monkeypatch.setattr(
        settings,
        "gemini_api_key",
        "test-key",
    )

    provider = get_ai_provider()

    assert isinstance(provider, GeminiAIProvider)


def test_factory_returns_openai_provider(monkeypatch):
    monkeypatch.setattr(
        settings,
        "ai_provider",
        "openai",
    )

    monkeypatch.setattr(
        settings,
        "openai_api_key",
        "test-key",
    )

    provider = get_ai_provider()

    assert isinstance(provider, OpenAIProvider)


def test_factory_returns_groq_provider(monkeypatch):
    monkeypatch.setattr(
        settings,
        "ai_provider",
        "groq",
    )

    monkeypatch.setattr(
        settings,
        "groq_api_key",
        "test-key",
    )

    provider = get_ai_provider()

    assert isinstance(provider, GroqAIProvider)


def test_factory_rejects_unknown_provider(monkeypatch):
    monkeypatch.setattr(
        settings,
        "ai_provider",
        "unknown",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported AI provider",
    ):
        get_ai_provider()