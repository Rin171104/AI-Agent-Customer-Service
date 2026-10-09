"""
LLM Client - Unified interface for LLM providers
"""
from abc import ABC, abstractmethod
from typing import Optional, Any
import asyncio

from src.utils.config import settings
from src.utils.logger import logger


# ============================================================
# EXCEPTIONS
# ============================================================

class LLMError(Exception):
    """Base exception for LLM errors"""
    pass


class LLMConfigurationError(LLMError):
    """Configuration error (missing API key, invalid model, etc.)"""
    pass


class LLMAuthenticationError(LLMError):
    """Authentication error (invalid API key)"""
    pass


class LLMRateLimitError(LLMError):
    """Rate limit error"""
    pass


class LLMTimeoutError(LLMError):
    """Timeout error"""
    pass


class LLMProviderError(LLMError):
    """Provider error (server error, etc.)"""
    pass


class LLMEmptyResponseError(LLMError):
    """Empty or invalid response from provider"""
    pass


# ============================================================
# PROVIDER INTERFACE
# ============================================================

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from prompt."""

    @abstractmethod
    async def generate_with_messages(
        self,
        messages: list[dict[str, str]],
        **kwargs
    ) -> str:
        """Generate response from message list."""


# ============================================================
# MOCK PROVIDER (for testing/development)
# ============================================================

class MockProvider(LLMProvider):
    """Mock provider for testing without API key."""

    def __init__(self, model: str = "mock"):
        self.model = model

    async def generate(self, prompt: str, **kwargs) -> str:
        """Return mock response."""
        logger.info(f"MockProvider generate: {prompt[:100]}...")
        return "Mock response - This is a simulated LLM response."

    async def generate_with_messages(
        self,
        messages: list[dict[str, str]],
        **kwargs
    ) -> str:
        """Return mock response from message history."""
        logger.info(f"MockProvider generate_with_messages: {len(messages)} messages")
        return "Mock response - This is a simulated LLM response."


# ============================================================
# OPENAI PROVIDER
# ============================================================

class OpenAIClient(LLMProvider):
    """OpenAI GPT client with real API integration."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini", timeout: int = 30):
        if not api_key or not api_key.strip():
            raise LLMConfigurationError(
                "OPENAI_API_KEY is required but not configured."
            )

        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self._client = None

    def _get_client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(
                    api_key=self.api_key,
                    timeout=self.timeout,
                    max_retries=0,  # We handle retries ourselves if needed
                )
            except ImportError:
                raise LLMConfigurationError(
                    "OpenAI SDK not installed. Run: pip install openai>=1.12.0"
                )
        return self._client

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI."""
        messages = [{"role": "user", "content": prompt}]
        return await self.generate_with_messages(messages, **kwargs)

    async def generate_with_messages(
        self,
        messages: list[dict[str, str]],
        **kwargs
    ) -> str:
        """Generate response using message history with OpenAI."""
        client = self._get_client()

        try:
            # Log without exposing API key
            logger.info(f"OpenAI request: model={self.model}, messages={len(messages)}")

            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    **kwargs
                ),
                timeout=self.timeout
            )

            # Extract response content
            if not response.choices:
                raise LLMEmptyResponseError("Empty response from OpenAI")

            content = response.choices[0].message.content

            if not content:
                raise LLMEmptyResponseError("No content in OpenAI response")

            logger.info(f"OpenAI response: {content[:100]}...")
            return content

        except asyncio.TimeoutError:
            raise LLMTimeoutError(f"OpenAI request timed out after {self.timeout}s")

        except self._get_openai_error_type() as e:
            error_type = type(e).__name__

            # Handle specific OpenAI errors
            if "api_key" in str(e).lower() or "authentication" in str(e).lower():
                raise LLMAuthenticationError(
                    "OpenAI authentication failed. Please check your API key."
                ) from e

            if "rate_limit" in str(e).lower() or "429" in str(e):
                raise LLMRateLimitError(
                    "OpenAI rate limit exceeded. Please try again later."
                ) from e

            if "500" in str(e) or "502" in str(e) or "503" in str(e):
                raise LLMProviderError(
                    f"OpenAI server error: {error_type}"
                ) from e

            # Generic provider error
            raise LLMProviderError(f"OpenAI error: {error_type}") from e

        except Exception as e:
            logger.error(f"Unexpected OpenAI error: {type(e).__name__}: {e}")
            raise LLMProviderError(f"Unexpected error: {type(e).__name__}") from e

    def _get_openai_error_type(self):
        """Get OpenAI exception types dynamically."""
        try:
            from openai import AuthenticationError, RateLimitError, Timeout, APIError
            return (AuthenticationError, RateLimitError, Timeout, APIError)
        except ImportError:
            return Exception


# ============================================================
# ANTHROPIC PROVIDER (Stub - for future)
# ============================================================

class AnthropicClient(LLMProvider):
    """Anthropic Claude client (stub - not implemented yet)."""

    def __init__(self, api_key: str, model: str = "claude-3-sonnet"):
        self.api_key = api_key
        self.model = model
        logger.warning("Anthropic provider is not yet implemented. Using mock response.")

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using Anthropic."""
        logger.info(f"Anthropic generate: {prompt[:100]}...")
        return "Mock response - Anthropic not yet implemented."

    async def generate_with_messages(
        self,
        messages: list[dict[str, str]],
        **kwargs
    ) -> str:
        """Generate response using message history."""
        logger.info(f"Anthropic generate_with_messages: {len(messages)} messages")
        return "Mock response - Anthropic not yet implemented."


# ============================================================
# PROVIDER FACTORY
# ============================================================

class LLMClient:
    """
    Unified LLM client with provider abstraction.

    Supports:
    - mock (for testing/development)
    - openai (GPT-4, GPT-3.5)
    - anthropic (Claude - stub)
    """

    def __init__(self):
        self.provider = self._create_provider()

    def _create_provider(self) -> LLMProvider:
        """Create LLM provider based on configuration."""
        provider = settings.LLM_PROVIDER.lower()

        if provider == "mock":
            logger.info("Using MockProvider for LLM")
            return MockProvider(model=settings.LLM_MODEL)

        elif provider == "openai":
            return OpenAIClient(
                api_key=settings.OPENAI_API_KEY,
                model=settings.LLM_MODEL or "gpt-4o-mini",
                timeout=settings.LLM_TIMEOUT_SECONDS,
            )

        elif provider == "anthropic":
            return AnthropicClient(
                api_key=settings.ANTHROPIC_API_KEY,
                model=settings.LLM_MODEL or "claude-3-sonnet",
            )

        else:
            raise LLMConfigurationError(
                f"Unsupported LLM provider: {provider}. "
                f"Supported: mock, openai, anthropic"
            )

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from prompt."""
        return await self.provider.generate(prompt, **kwargs)

    async def generate_with_messages(
        self,
        messages: list[dict[str, str]],
        **kwargs
    ) -> str:
        """Generate response from message history."""
        return await self.provider.generate_with_messages(messages, **kwargs)
