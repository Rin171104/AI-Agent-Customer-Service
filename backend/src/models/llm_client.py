"""
LLM Client - Unified interface for LLM providers
"""
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

from src.utils.config import settings
from src.utils.logger import logger


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from prompt."""
        pass

    @abstractmethod
    async def generate_with_messages(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Generate response from message list."""
        pass


class OpenAIClient(LLMProvider):
    """OpenAI GPT client."""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        # TODO: Initialize OpenAI client

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI."""
        logger.info(f"OpenAI generate: {prompt[:100]}...")
        # TODO: Implement actual API call
        return "Mock response"

    async def generate_with_messages(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Generate response using message history."""
        logger.info(f"OpenAI generate_with_messages: {len(messages)} messages")
        # TODO: Implement actual API call
        return "Mock response"


class AnthropicClient(LLMProvider):
    """Anthropic Claude client."""

    def __init__(self, api_key: str, model: str = "claude-3-sonnet"):
        self.api_key = api_key
        self.model = model
        # TODO: Initialize Anthropic client

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using Anthropic."""
        logger.info(f"Anthropic generate: {prompt[:100]}...")
        # TODO: Implement actual API call
        return "Mock response"

    async def generate_with_messages(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Generate response using message history."""
        logger.info(f"Anthropic generate_with_messages: {len(messages)} messages")
        # TODO: Implement actual API call
        return "Mock response"


class LLMClient:
    """
    Unified LLM client with provider abstraction.

    Supports:
    - OpenAI (GPT-4, GPT-3.5)
    - Anthropic (Claude)
    """

    def __init__(self):
        self.provider = self._create_provider()

    def _create_provider(self) -> LLMProvider:
        """Create LLM provider based on configuration."""
        provider = settings.LLM_PROVIDER.lower()

        if provider == "openai":
            return OpenAIClient(
                api_key=settings.OPENAI_API_KEY,
                model=settings.LLM_MODEL or "gpt-4",
            )
        elif provider == "anthropic":
            return AnthropicClient(
                api_key=settings.ANTHROPIC_API_KEY,
                model=settings.LLM_MODEL or "claude-3-sonnet",
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from prompt."""
        return await self.provider.generate(prompt, **kwargs)

    async def generate_with_messages(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Generate response from message history."""
        return await self.provider.generate_with_messages(messages, **kwargs)
