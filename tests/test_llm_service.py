"""Unit tests for TasteMatch AI LLM Switcher & Service."""

from unittest.mock import MagicMock, patch
import pytest
from pydantic import BaseModel, Field

from src.config import LLMSettings
from src.llm.models import LLMProviderEnum, LLMResponse
from src.llm.providers import format_litellm_model_name, get_default_model
from src.llm.service import LLMService
from src.llm.health import LLMHealthChecker


def test_provider_defaults():
    """Verify default model assignments for each provider."""
    assert get_default_model(LLMProviderEnum.OPENAI) == "gpt-4o-mini"
    assert get_default_model(LLMProviderEnum.CLAUDE) == "claude-3-5-sonnet-20241022"
    assert get_default_model(LLMProviderEnum.OLLAMA) == "llama3.2"
    assert get_default_model(LLMProviderEnum.GEMINI) == "gemini-1.5-flash"


def test_litellm_model_formatting():
    """Verify LiteLLM format string translation."""
    assert (
        format_litellm_model_name(LLMProviderEnum.OPENAI, "gpt-4o") == "openai/gpt-4o"
    )
    assert (
        format_litellm_model_name(LLMProviderEnum.CLAUDE, "claude-3-haiku")
        == "anthropic/claude-3-haiku"
    )
    assert (
        format_litellm_model_name(LLMProviderEnum.OLLAMA, "mistral") == "ollama/mistral"
    )
    assert (
        format_litellm_model_name(LLMProviderEnum.GEMINI, "gemini-1.5-pro")
        == "gemini/gemini-1.5-pro"
    )


def test_service_provider_switching():
    """Test dynamic provider switching at runtime."""
    settings = LLMSettings(LLM_PROVIDER="openai", LLM_MODEL="gpt-4o-mini")
    service = LLMService(settings=settings)

    assert service.active_provider == LLMProviderEnum.OPENAI
    assert service.active_model == "gpt-4o-mini"

    # Switch to Claude
    service.set_provider("claude")
    assert service.active_provider == LLMProviderEnum.CLAUDE
    assert service.active_model == "claude-3-5-sonnet-20241022"

    # Switch to Ollama with custom model
    service.set_provider("ollama", model="llama3.1:70b")
    assert service.active_provider == LLMProviderEnum.OLLAMA
    assert service.active_model == "llama3.1:70b"

    # Switch to Gemini
    service.set_provider("gemini")
    assert service.active_provider == LLMProviderEnum.GEMINI
    assert service.active_model == "gemini-1.5-flash"


@patch("litellm.completion")
def test_mock_generation(mock_completion):
    """Test text generation with mocked LiteLLM completion."""
    # Setup mock response object
    mock_choice = MagicMock()
    mock_choice.message.content = "Synthetic vibe playlist response"
    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 10
    mock_usage.completion_tokens = 15
    mock_usage.total_tokens = 25

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage = mock_usage
    mock_response.model_dump.return_value = {"id": "mock-123"}

    mock_completion.return_value = mock_response

    settings = LLMSettings(LLM_PROVIDER="openai", OPENAI_API_KEY="sk-fake-key")
    service = LLMService(settings=settings)

    res = service.generate("Recommend a dark synthwave playlist")

    assert isinstance(res, LLMResponse)
    assert res.content == "Synthetic vibe playlist response"
    assert res.provider == LLMProviderEnum.OPENAI
    assert res.prompt_tokens == 10
    assert res.completion_tokens == 15
    assert res.total_tokens == 25
    assert mock_completion.called


class SamplePlaylistSchema(BaseModel):
    title: str
    description: str
    suggested_artists: list[str]


@patch("litellm.completion")
def test_mock_structured_generation(mock_completion):
    """Test structured schema generation with mocked response."""
    mock_choice = MagicMock()
    mock_choice.message.content = '{"title": "Late Night Coding", "description": "Lo-fi beats", "suggested_artists": ["Tycho", "Kiasmos"]}'
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage = None
    mock_response.model_dump.return_value = {"id": "mock-structured-123"}

    mock_completion.return_value = mock_response

    settings = LLMSettings(LLM_PROVIDER="claude", ANTHROPIC_API_KEY="sk-ant-fake")
    service = LLMService(settings=settings)

    result = service.generate_structured("Create coding playlist", SamplePlaylistSchema)

    assert isinstance(result, SamplePlaylistSchema)
    assert result.title == "Late Night Coding"
    assert result.description == "Lo-fi beats"
    assert result.suggested_artists == ["Tycho", "Kiasmos"]


def test_health_checker_unconfigured():
    """Test health check behavior for unconfigured provider."""
    settings = LLMSettings(
        OPENAI_API_KEY="",
        ANTHROPIC_API_KEY="",
        GEMINI_API_KEY="",
    )
    checker = LLMHealthChecker(settings=settings)
    health = checker.check_provider(LLMProviderEnum.OPENAI)

    assert health.is_available is False
    assert "Not configured" in health.message
