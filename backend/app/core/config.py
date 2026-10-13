"""
Application configuration for DecisionOS.

Loads configuration values from environment variables
and the project's .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.
    """

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    app_name: str = "DecisionOS"
    app_env: str = "development"

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    database_url: str

    # ------------------------------------------------------------------
    # AI Provider
    # ------------------------------------------------------------------

    # Primary AI provider.
    #
    # Supported:
    # - mock
    # - gemini
    # - openai
    # - groq
    ai_provider: str = "mock"

    # Comma-separated fallback providers.
    #
    # Example:
    # "openai,groq"
    ai_fallback_providers: str = ""

    # ------------------------------------------------------------------
    # AI API Keys
    # ------------------------------------------------------------------

    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    groq_api_key: str | None = None

    # ------------------------------------------------------------------
    # AI Models
    # ------------------------------------------------------------------

    openai_model: str = "gpt-4o-mini"
    gemini_model: str = "gemini-3.8-flash"
    groq_model: str = "llama-3.3-70b-versatile"

    # ------------------------------------------------------------------
    # Environment configuration
    # ------------------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()