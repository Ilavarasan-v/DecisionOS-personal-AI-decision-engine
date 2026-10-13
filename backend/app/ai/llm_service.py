"""
Thin abstraction over multiple LLM providers (OpenAI, Gemini, Groq) so the
rest of the app can call `LLMService().complete(prompt)` without caring
which provider is configured.
"""

from backend.app.ai.providers import gemini, groq, openai
from backend.app.core.config import settings

_PROVIDERS = {
    "openai": openai.complete,
    "gemini": gemini.complete,
    "groq": groq.complete,
}


class LLMService:
    def __init__(self, provider: str | None = None):
        self.provider_name = provider or settings.DEFAULT_LLM_PROVIDER
        if self.provider_name not in _PROVIDERS:
            raise ValueError(
                f"Unknown LLM provider '{self.provider_name}'. "
                f"Choose one of: {list(_PROVIDERS)}"
            )

    def complete(self, prompt: str, **kwargs) -> str:
        """Send a prompt to the configured provider and return the completion text."""
        provider_fn = _PROVIDERS[self.provider_name]
        return provider_fn(prompt, **kwargs)
