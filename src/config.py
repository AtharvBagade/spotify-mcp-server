"""Configuration settings management using Pydantic Settings."""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.llm.models import LLMProviderEnum
from src.llm.providers import get_default_model, format_litellm_model_name


class LLMSettings(BaseSettings):
    """Application configuration for TasteMatch AI LLM gateway."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Active LLM Switcher settings
    llm_provider: LLMProviderEnum = Field(
        default=LLMProviderEnum.OPENAI,
        alias="LLM_PROVIDER",
        description="Active LLM provider: openai | claude | ollama | gemini",
    )
    llm_model: Optional[str] = Field(
        default="",
        alias="LLM_MODEL",
        description="Optional model override. Uses provider default if empty.",
    )
    llm_enable_fallback: bool = Field(
        default=True,
        alias="LLM_ENABLE_FALLBACK",
        description="Enable automatic fallback to another available provider on failure.",
    )

    # API Keys
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")

    # Local Ollama Provider settings
    local_llm_base_url: str = Field(
        default="http://localhost:11434",
        alias="LOCAL_LLM_BASE_URL",
        description="Base URL for local Ollama host.",
    )
    ollama_model: str = Field(
        default="llama3.2",
        alias="OLLAMA_MODEL",
        description="Default local Ollama model.",
    )

    # Spotify Integration Credentials (Placeholder for future milestones)
    spotify_client_id: Optional[str] = Field(default=None, alias="SPOTIFY_CLIENT_ID")
    spotify_client_secret: Optional[str] = Field(
        default=None, alias="SPOTIFY_CLIENT_SECRET"
    )
    spotify_redirect_uri: str = Field(
        default="http://localhost:3000/auth/callback",
        alias="SPOTIFY_REDIRECT_URI",
    )

    def get_active_model(self) -> str:
        """Returns active model for the current provider."""
        if self.llm_model and self.llm_model.strip():
            return self.llm_model.strip()
        if self.llm_provider == LLMProviderEnum.OLLAMA and self.ollama_model:
            return self.ollama_model
        return get_default_model(self.llm_provider)

    def get_litellm_model(self) -> str:
        """Returns the LiteLLM formatted model string."""
        return format_litellm_model_name(self.llm_provider, self.get_active_model())

    def get_api_key(self, provider: Optional[LLMProviderEnum] = None) -> Optional[str]:
        """Fetch API key for specified provider or active provider."""
        target_provider = provider or self.llm_provider
        if target_provider == LLMProviderEnum.OPENAI:
            return self.openai_api_key
        elif target_provider == LLMProviderEnum.CLAUDE:
            return self.anthropic_api_key
        elif target_provider == LLMProviderEnum.GEMINI:
            return self.gemini_api_key
        return None

    def is_provider_configured(self, provider: LLMProviderEnum) -> bool:
        """Check if required credentials/base URL exist for a provider."""
        if provider == LLMProviderEnum.OPENAI:
            return bool(self.openai_api_key and self.openai_api_key.strip())
        elif provider == LLMProviderEnum.CLAUDE:
            return bool(self.anthropic_api_key and self.anthropic_api_key.strip())
        elif provider == LLMProviderEnum.GEMINI:
            return bool(self.gemini_api_key and self.gemini_api_key.strip())
        elif provider == LLMProviderEnum.OLLAMA:
            return bool(self.local_llm_base_url and self.local_llm_base_url.strip())
        return False


def load_settings() -> LLMSettings:
    """Helper factory to load current application settings."""
    return LLMSettings()
