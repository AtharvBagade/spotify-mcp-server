"""Health checker module for diagnosing LLM provider connectivity and key validity."""

import time
import logging
from typing import Dict, Optional, TYPE_CHECKING
import litellm

from src.llm.models import LLMProviderEnum, ProviderHealth
from src.llm.providers import format_litellm_model_name, get_default_model

if TYPE_CHECKING:
    from src.config import LLMSettings

logger = logging.getLogger(__name__)


class LLMHealthChecker:
    """Diagnostic tool to verify credentials and connectivity for LLM providers."""

    def __init__(self, settings: Optional["LLMSettings"] = None):
        if settings is None:
            from src.config import load_settings

            settings = load_settings()
        self.settings: "LLMSettings" = settings

    def check_provider(
        self,
        provider: LLMProviderEnum,
        model: Optional[str] = None,
    ) -> ProviderHealth:
        """Run a minimal 1-token diagnostic test call to verify provider reachability."""
        target_model = model or get_default_model(provider)
        litellm_model = format_litellm_model_name(provider, target_model)

        if not self.settings.is_provider_configured(provider):
            return ProviderHealth(
                provider=provider,
                model=target_model,
                is_available=False,
                latency_ms=None,
                message="Not configured (missing API Key or base URL)",
            )

        call_kwargs = {
            "model": litellm_model,
            "messages": [{"role": "user", "content": "Respond with the word 'OK'."}],
            "max_tokens": 5,
            "timeout": 10,
        }

        if provider == LLMProviderEnum.OPENAI:
            call_kwargs["api_key"] = self.settings.openai_api_key
        elif provider == LLMProviderEnum.CLAUDE:
            call_kwargs["api_key"] = self.settings.anthropic_api_key
        elif provider == LLMProviderEnum.GEMINI:
            call_kwargs["api_key"] = self.settings.gemini_api_key
        elif provider == LLMProviderEnum.OLLAMA:
            call_kwargs["api_base"] = self.settings.local_llm_base_url

        try:
            start_time = time.perf_counter()
            response = litellm.completion(**call_kwargs)
            latency = (time.perf_counter() - start_time) * 1000.0

            content = response.choices[0].message.content or ""
            return ProviderHealth(
                provider=provider,
                model=target_model,
                is_available=True,
                latency_ms=round(latency, 2),
                message=f"Connected successfully ({content.strip()})",
            )
        except Exception as e:
            error_msg = str(e)
            if (
                "AuthenticationError" in error_msg
                or "invalid_api_key" in error_msg
                or "401" in error_msg
            ):
                user_msg = "Authentication Failed: Invalid API Key"
            elif "ConnectionError" in error_msg or "Failed to connect" in error_msg:
                user_msg = "Connection Failed: Host unreachable (Is Ollama running?)"
            else:
                user_msg = f"Error: {error_msg[:80]}"

            return ProviderHealth(
                provider=provider,
                model=target_model,
                is_available=False,
                latency_ms=None,
                message=user_msg,
            )

    def check_all(self) -> Dict[LLMProviderEnum, ProviderHealth]:
        """Test health across all supported LLM providers."""
        results = {}
        for provider in LLMProviderEnum:
            results[provider] = self.check_provider(provider)
        return results
