"""Provider registry metadata and LiteLLM model string translation."""

from typing import Dict, Optional
from src.llm.models import LLMProviderEnum

DEFAULT_MODELS: Dict[LLMProviderEnum, str] = {
    LLMProviderEnum.OPENAI: "gpt-4o-mini",
    LLMProviderEnum.CLAUDE: "claude-3-5-sonnet-20241022",
    LLMProviderEnum.OLLAMA: "llama3.2",
    LLMProviderEnum.GEMINI: "gemini-1.5-flash",
}


def get_default_model(provider: LLMProviderEnum) -> str:
    """Retrieve default model identifier for a provider."""
    return DEFAULT_MODELS.get(provider, "gpt-4o-mini")


def format_litellm_model_name(
    provider: LLMProviderEnum, model: Optional[str] = None
) -> str:
    """Format provider and model name into LiteLLM format string.

    Examples:
    - OpenAI: 'openai/gpt-4o-mini' or 'gpt-4o-mini'
    - Claude: 'anthropic/claude-3-5-sonnet-20241022'
    - Ollama: 'ollama/llama3.2'
    - Gemini: 'gemini/gemini-1.5-flash'
    """
    model_name = model if model and model.strip() else get_default_model(provider)

    # Strip any existing prefix if user provided it
    clean_model = model_name
    if "/" in model_name:
        clean_model = model_name.split("/", 1)[1]

    if provider == LLMProviderEnum.OPENAI:
        return (
            f"openai/{clean_model}"
            if not model_name.startswith("openai/")
            else model_name
        )
    elif provider == LLMProviderEnum.CLAUDE:
        return (
            f"anthropic/{clean_model}"
            if not model_name.startswith("anthropic/")
            else model_name
        )
    elif provider == LLMProviderEnum.OLLAMA:
        return (
            f"ollama/{clean_model}"
            if not model_name.startswith("ollama/")
            else model_name
        )
    elif provider == LLMProviderEnum.GEMINI:
        return (
            f"gemini/{clean_model}"
            if not model_name.startswith("gemini/")
            else model_name
        )

    return model_name
