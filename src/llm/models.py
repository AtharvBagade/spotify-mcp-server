"""Standardized data models and exception types for LLM operations."""

from enum import Enum
from typing import Any, Dict, Optional, Literal
from pydantic import BaseModel, Field


class LLMProviderEnum(str, Enum):
    """Supported LLM Providers."""

    OPENAI = "openai"
    CLAUDE = "claude"
    OLLAMA = "ollama"
    GEMINI = "gemini"


class LLMMessage(BaseModel):
    """Standardized chat message payload."""

    role: Literal["system", "user", "assistant"] = "user"
    content: str


class LLMResponse(BaseModel):
    """Unified response object across all LLM providers."""

    content: str = Field(description="Generated text response")
    provider: LLMProviderEnum = Field(description="Active LLM provider used")
    model: str = Field(description="Model identifier executed")
    prompt_tokens: int = Field(default=0, description="Tokens in input prompt")
    completion_tokens: int = Field(default=0, description="Tokens in output response")
    total_tokens: int = Field(default=0, description="Total tokens consumed")
    latency_ms: float = Field(default=0.0, description="Execution time in milliseconds")
    raw_response: Optional[Dict[str, Any]] = Field(
        default=None, description="Original SDK response payload"
    )


class ProviderHealth(BaseModel):
    """Diagnostic health status for a provider."""

    provider: LLMProviderEnum
    model: str
    is_available: bool
    latency_ms: Optional[float] = None
    message: str


class LLMProviderError(Exception):
    """Base exception for provider generation errors."""

    def __init__(
        self,
        provider: LLMProviderEnum,
        message: str,
        original_error: Optional[Exception] = None,
    ):
        self.provider = provider
        self.message = message
        self.original_error = original_error
        super().__init__(f"[{provider.value.upper()}] Error: {message}")


class LLMHealthCheckError(LLMProviderError):
    """Exception raised when health check fails."""

    pass


class LLMStructuredOutputError(LLMProviderError):
    """Exception raised when structured output parsing fails."""

    pass
