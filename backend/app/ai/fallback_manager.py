"""
AI provider fallback manager for DecisionOS.

Attempts AI providers in configured order and falls back
to the next provider when the current provider fails.
"""

from typing import Any

from backend.app.ai.providers.factory import get_ai_provider
from backend.app.ai.providers.base import AIProvider
from backend.app.core.config import settings


class AIFallbackManager:
    """
    Coordinates multiple AI providers with automatic fallback.

    The primary provider is taken from AI_PROVIDER.
    Additional providers are taken from
    AI_FALLBACK_PROVIDERS.
    """

    def __init__(self) -> None:
        self.provider_names = self._build_provider_order()

    @staticmethod
    def _build_provider_order() -> list[str]:
        """
        Build the provider execution order.

        The configured primary provider is always first.
        Duplicate providers are removed while preserving order.
        """

        primary = settings.ai_provider.lower().strip()

        fallback_names = [
            provider.strip().lower()
            for provider in settings.ai_fallback_providers.split(",")
            if provider.strip()
        ]

        provider_order = [primary]

        for provider_name in fallback_names:
            if provider_name not in provider_order:
                provider_order.append(provider_name)

        return provider_order

    def generate_explanation(
        self,
        decision_context: dict[str, Any],
    ) -> str:
        """
        Try each configured provider in order.

        Returns the first successful explanation.

        Raises:
            RuntimeError: If every configured provider fails.
        """

        errors: list[str] = []

        for provider_name in self.provider_names:
            try:
                provider = self._create_provider(provider_name)

                return provider.generate_explanation(
                    decision_context
                )

            except Exception as exc:
                errors.append(
                    f"{provider_name}: {exc}"
                )

        error_details = "; ".join(errors)

        raise RuntimeError(
            "All configured AI providers failed. "
            f"Details: {error_details}"
        )

    @staticmethod
    def _create_provider(
        provider_name: str,
    ) -> AIProvider:
        """
        Create a specific provider using the existing
        provider factory configuration.
        """

        original_provider = settings.ai_provider

        try:
            settings.ai_provider = provider_name

            return get_ai_provider()

        finally:
            settings.ai_provider = original_provider