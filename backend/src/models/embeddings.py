"""
Embeddings - Text embedding utilities
"""
from typing import List, Optional
from abc import ABC, abstractmethod

from src.utils.config import settings
from src.utils.logger import logger


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        pass


class OpenAIEmbeddings(EmbeddingProvider):
    """OpenAI text embeddings."""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model

    async def embed(self, text: str) -> List[float]:
        """Generate embedding using OpenAI."""
        logger.info(f"OpenAI embed: {text[:50]}...")
        # TODO: Implement actual API call
        # Return mock embedding
        return [0.1] * 1536

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        logger.info(f"OpenAI embed_batch: {len(texts)} texts")
        # TODO: Implement actual API call
        return [[0.1] * 1536 for _ in texts]


class Embeddings:
    """
    Unified embeddings client.
    """

    def __init__(self):
        self.provider = self._create_provider()

    def _create_provider(self) -> EmbeddingProvider:
        """Create embedding provider based on configuration."""
        model = settings.EMBEDDING_MODEL

        if "openai" in model.lower() or "text-embedding" in model.lower():
            return OpenAIEmbeddings(
                api_key=settings.OPENAI_API_KEY,
                model=model,
            )
        else:
            raise ValueError(f"Unsupported embedding model: {model}")

    async def embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        return await self.provider.embed(text)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        return await self.provider.embed_batch(texts)
