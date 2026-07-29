"""Unified LLM Service wrapping LiteLLM with runtime switching and fallback capabilities."""

import time
import json
import logging
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, TYPE_CHECKING
from pydantic import BaseModel

import litellm
from src.llm.models import (
    LLMProviderEnum,
    LLMMessage,
    LLMResponse,
    LLMProviderError,
    LLMStructuredOutputError,
)
from src.llm.providers import format_litellm_model_name, get_default_model

if TYPE_CHECKING:
    from src.config import LLMSettings

# Silence noisy verbose logs from LiteLLM by default
litellm.suppress_debug_info = True

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)


class LLMService:
    """Unified service layer for managing and executing LLM requests across providers."""

    def __init__(self, settings: Optional["LLMSettings"] = None):
        if settings is None:
            from src.config import load_settings

            settings = load_settings()
        self.settings: "LLMSettings" = settings
        self._active_provider: LLMProviderEnum = self.settings.llm_provider
        self._active_model: str = self.settings.get_active_model()

    @property
    def active_provider(self) -> LLMProviderEnum:
        """Get currently active LLM provider."""
        return self._active_provider

    @property
    def active_model(self) -> str:
        """Get currently active model name."""
        return self._active_model

    def set_provider(
        self, provider: Union[str, LLMProviderEnum], model: Optional[str] = None
    ) -> None:
        """Dynamically switch active LLM provider and optionally model."""
        if isinstance(provider, str):
            provider = LLMProviderEnum(provider.lower())

        self._active_provider = provider
        if model and model.strip():
            self._active_model = model.strip()
        else:
            self._active_model = get_default_model(provider)

        logger.info(
            f"Switched active provider to [{self._active_provider.value}] with model [{self._active_model}]"
        )

    def get_status(self) -> Dict[str, Any]:
        """Return runtime status of providers and API key availability."""
        configured_providers = {
            p.value: self.settings.is_provider_configured(p) for p in LLMProviderEnum
        }
        return {
            "active_provider": self._active_provider.value,
            "active_model": self._active_model,
            "litellm_model_string": format_litellm_model_name(
                self._active_provider, self._active_model
            ),
            "fallback_enabled": self.settings.llm_enable_fallback,
            "configured_providers": configured_providers,
            "ollama_base_url": self.settings.local_llm_base_url,
        }

    def _prepare_kwargs(
        self,
        provider: LLMProviderEnum,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Construct LiteLLM completion arguments."""
        model_str = format_litellm_model_name(provider, model)

        call_kwargs: Dict[str, Any] = {
            "model": model_str,
            "messages": messages,
            "temperature": temperature,
            **kwargs,
        }

        # Inject specific provider credentials & endpoints
        if provider == LLMProviderEnum.OPENAI and self.settings.openai_api_key:
            call_kwargs["api_key"] = self.settings.openai_api_key
        elif provider == LLMProviderEnum.CLAUDE and self.settings.anthropic_api_key:
            call_kwargs["api_key"] = self.settings.anthropic_api_key
        elif provider == LLMProviderEnum.GEMINI and self.settings.gemini_api_key:
            call_kwargs["api_key"] = self.settings.gemini_api_key
        elif provider == LLMProviderEnum.OLLAMA:
            call_kwargs["api_base"] = self.settings.local_llm_base_url

        return call_kwargs

    def _normalize_messages(
        self,
        prompt: Union[str, List[Union[LLMMessage, Dict[str, str]]]],
        system_prompt: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """Format input into standard list of role/content dictionaries."""
        messages: List[Dict[str, str]] = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if isinstance(prompt, str):
            messages.append({"role": "user", "content": prompt})
        elif isinstance(prompt, list):
            for msg in prompt:
                if isinstance(msg, LLMMessage):
                    messages.append({"role": msg.role, "content": msg.content})
                elif isinstance(msg, dict):
                    messages.append(
                        {
                            "role": msg.get("role", "user"),
                            "content": msg.get("content", ""),
                        }
                    )

        return messages

    def generate(
        self,
        prompt: Union[str, List[Union[LLMMessage, Dict[str, str]]]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate text completion using active LLM provider, with optional fallback."""
        messages = self._normalize_messages(prompt, system_prompt)
        providers_to_try = [self._active_provider]

        # Add fallback providers if enabled and configured
        if self.settings.llm_enable_fallback:
            for candidate in LLMProviderEnum:
                if (
                    candidate not in providers_to_try
                    and self.settings.is_provider_configured(candidate)
                ):
                    providers_to_try.append(candidate)

        last_exception: Optional[Exception] = None

        for current_provider in providers_to_try:
            current_model = (
                self._active_model
                if current_provider == self._active_provider
                else get_default_model(current_provider)
            )

            call_kwargs = self._prepare_kwargs(
                current_provider, current_model, messages, temperature, **kwargs
            )

            try:
                start_time = time.perf_counter()
                response = litellm.completion(**call_kwargs)
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0

                # Extract text content and token usage safely
                choice = response.choices[0]
                content = choice.message.content or ""
                usage = getattr(response, "usage", None)

                prompt_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
                completion_tokens = (
                    getattr(usage, "completion_tokens", 0) if usage else 0
                )
                total_tokens = getattr(usage, "total_tokens", 0) if usage else 0

                raw_resp = None
                if hasattr(response, "model_dump") and callable(response.model_dump):
                    try:
                        dumped = response.model_dump()
                        if isinstance(dumped, dict):
                            raw_resp = dumped
                    except Exception:
                        raw_resp = None

                return LLMResponse(
                    content=content,
                    provider=current_provider,
                    model=current_model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    latency_ms=round(elapsed_ms, 2),
                    raw_response=raw_resp,
                )

            except Exception as e:
                logger.warning(
                    f"Generation failed for provider [{current_provider.value}] (Model: {current_model}): {e}"
                )
                last_exception = e
                # Continue loop to try next fallback provider

        raise LLMProviderError(
            provider=self._active_provider,
            message=f"All attempted providers failed. Last error: {last_exception}",
            original_error=last_exception,
        )

    def generate_structured(
        self,
        prompt: Union[str, List[Union[LLMMessage, Dict[str, str]]]],
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> T:
        """Generate structured data parsed directly into a Pydantic model."""
        schema_json = json.dumps(response_model.model_json_schema(), indent=2)
        system_instruction = (
            f"{system_prompt or ''}\n\n"
            f"CRITICAL INSTRUCTION: You MUST return your response as a valid JSON object strictly adhering "
            f"to the following JSON Schema:\n{schema_json}\n"
            f"Do not include markdown code block formatting (```json) or introductory text."
        ).strip()

        # Attempt generation using response_format if supported, or schema prompt injection
        try:
            response = self.generate(
                prompt=prompt,
                system_prompt=system_instruction,
                temperature=temperature,
                response_format={"type": "json_object"},
            )
            raw_text = response.content.strip()

            # Clean markdown codeblocks if LLM returned them
            if raw_text.startswith("```"):
                lines = raw_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_text = "\n".join(lines).strip()

            parsed_data = json.loads(raw_text)
            return response_model.model_validate(parsed_data)

        except Exception as e:
            raise LLMStructuredOutputError(
                provider=self._active_provider,
                message=f"Failed to parse structured output for model {response_model.__name__}: {e}",
                original_error=e,
            )
