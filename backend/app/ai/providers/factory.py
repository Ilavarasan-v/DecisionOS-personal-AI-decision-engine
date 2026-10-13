"""
AI provider factory for DecisionOS.

Selects the configured AI provider without exposing
provider-specific implementation details to the API layer.
"""

from backend.app.ai.providers.base import AIProvider
from backend.app.ai.providers.gemini import GeminiAIProvider
from backend.app.ai.providers.groq import GroqAIProvider
from backend.app.ai.providers.mock import MockAIProvider
from backend.app.ai.providers.openai import OpenAIProvider
from backend.app.core.config import settings


def get_ai_provider() -> AIProvider:
    """
    Return the AI provider configured for the application.

    Supported providers:
    - mock
    - gemini
    - openai
    - groq
    """

    provider_name = settings.ai_provider.lower().strip()

    if provider_name == "mock":
        return MockAIProvider()

    if provider_name == "gemini":
        return GeminiAIProvider()

    if provider_name == "openai":
        return OpenAIProvider()

    if provider_name == "groq":
        return GroqAIProvider()

    raise ValueError(
        f"Unsupported AI provider: {provider_name}"
    )