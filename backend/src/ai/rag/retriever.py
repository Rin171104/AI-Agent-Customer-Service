"""
Knowledge Retriever - RAG search tool cho AI agents

CHỈ dùng cho KNOWLEDGE - KHÔNG dùng cho realtime data.

Security:
    - Read-only, không modify database
    - Không call business logic
    - Không execute transactions
    - Prompt injection protection via sanitization
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np

from src.ai.rag.loader import load_knowledge_documents
from src.ai.rag.chunker import chunk_documents, MarkdownChunker
from src.ai.rag.embeddings import get_embeddings_generator
from src.ai.rag.vector_store import get_vector_store
from src.utils.logger import logger


# Configuration
RAG_TOP_K = 5  # Number of results to return
RAG_SCORE_THRESHOLD = 0.3  # Minimum similarity score (baseline, adjust after evaluation)


@dataclass
class RetrievalResult:
    """Kết quả retrieval"""
    content: str
    source: str
    document: str
    section: str
    score: float
    chunk_id: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "source": self.source,
            "document": self.document,
            "section": self.section,
            "score": self.score,
            "chunk_id": self.chunk_id,
        }


class KnowledgeRetriever:
    """
    Knowledge Retriever - RAG search tool.

    IMPORTANT:
    - CHỈ dùng cho knowledge/FAQ/policy queries
    - KHÔNG dùng cho realtime booking/payment status
    - Read-only - không modify anything
    """

    def __init__(
        self,
        top_k: int = RAG_TOP_K,
        score_threshold: float = RAG_SCORE_THRESHOLD
    ):
        self.top_k = top_k
        self.score_threshold = score_threshold
        self.embeddings_generator = None
        self.vector_store = None
        self._initialized = False

    def initialize(self, force_rebuild: bool = False):
        """
        Initialize RAG index.

        Args:
            force_rebuild: Force rebuild index even if exists
        """
        if self._initialized and not force_rebuild:
            return

        logger.info("Initializing RAG knowledge base...")

        # Load documents
        try:
            documents = load_knowledge_documents()
            logger.info(f"Loaded {len(documents)} documents")
        except FileNotFoundError as e:
            logger.error(f"Knowledge directory not found: {e}")
            documents = []

        if not documents:
            logger.warning("No documents loaded")
            self._initialized = True
            return

        # Chunk documents
        chunker = MarkdownChunker(min_chunk_size=50, max_chunk_size=800)
        chunks = chunk_documents(documents, chunker)
        logger.info(f"Created {len(chunks)} chunks")

        # Generate embeddings
        self.embeddings_generator = get_embeddings_generator()
        texts = [c.content for c in chunks]
        embeddings = self.embeddings_generator.embed_batch(texts)
        logger.info(f"Generated {len(embeddings)} embeddings")

        # Store metadata
        metadatas = [
            {
                "source": c.source,
                "document": c.document,
                "section": c.section,
                "chunk_id": c.chunk_id
            }
            for c in chunks
        ]

        # Add to vector store
        self.vector_store = get_vector_store()
        self.vector_store.add(texts, embeddings, metadatas)
        self.vector_store.persist()

        self._initialized = True
        logger.info("RAG knowledge base initialized")

    def search(
        self,
        query: str,
        top_k: int = None,
        score_threshold: float = None
    ) -> List[RetrievalResult]:
        """
        Search knowledge base.

        Args:
            query: Search query
            top_k: Number of results (overrides default)
            score_threshold: Minimum score (overrides default)

        Returns:
            List of RetrievalResult
        """
        if not self._initialized:
            self.initialize()

        if self.vector_store is None:
            return []

        top_k = top_k or self.top_k
        score_threshold = score_threshold or self.score_threshold

        # Sanitize query (basic prompt injection protection)
        query = self._sanitize_query(query)

        # Generate query embedding
        if self.embeddings_generator is None:
            self.embeddings_generator = get_embeddings_generator()

        query_embedding = self.embeddings_generator.embed(query)

        # Search
        results = self.vector_store.search(
            query_embedding=query_embedding,
            k=top_k,
            threshold=score_threshold
        )

        # Convert to RetrievalResult
        retrieval_results = []
        for r in results:
            retrieval_results.append(RetrievalResult(
                content=r["content"],
                source=r["source"],
                document=r["document"],
                section=r["section"],
                score=r["score"],
                chunk_id=r["chunk_id"]
            ))

        logger.info(f"RAG search for '{query[:50]}...': {len(retrieval_results)} results")

        return retrieval_results

    def search_with_context(
        self,
        query: str,
        top_k: int = None
    ) -> Dict[str, Any]:
        """
        Search and format results for agent consumption.

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            Dict with results and formatted context
        """
        results = self.search(query, top_k=top_k)

        if not results:
            return {
                "success": False,
                "status": "NO_KNOWLEDGE",
                "response": "Tôi chưa tìm thấy thông tin phù hợp trong dữ liệu của nhà xe.",
                "results": []
            }

        # Format context for agent
        context_parts = []
        sources = []

        for i, r in enumerate(results, 1):
            context_parts.append(
                f"[{i}] {r.section}\n"
                f"Source: {r.source}\n"
                f"{r.content}\n"
            )
            sources.append({
                "source": r.source,
                "section": r.section,
                "score": round(r.score, 3)
            })

        context = "\n---\n".join(context_parts)

        return {
            "success": True,
            "results": [r.to_dict() for r in results],
            "context": context,
            "sources": sources,
            "count": len(results)
        }

    def _sanitize_query(self, query: str) -> str:
        """
        Basic prompt injection protection.
        Remove common injection patterns.
        """
        # Remove obvious instruction overrides
        dangerous_patterns = [
            r"ignore\s+(previous|all)\s+(instructions?|prompt)",
            r"disregard\s+(previous|all)\s+(instructions?|prompt)",
            r"forget\s+(previous|all)\s+(instructions?|prompt)",
            r"system\s*:\s*",
            r"you\s+are\s+a?\s*(different|new|evil)",
        ]

        sanitized = query
        import re
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)

        # Limit length
        max_length = 500
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        return sanitized.strip()


# Singleton instance
_retriever = None


def get_knowledge_retriever() -> KnowledgeRetriever:
    """Get singleton retriever"""
    global _retriever
    if _retriever is None:
        _retriever = KnowledgeRetriever()
        _retriever.initialize()
    return _retriever


async def search_knowledge(
    query: str,
    top_k: int = RAG_TOP_K
) -> Dict[str, Any]:
    """
    Convenience function for agents to search knowledge.

    Args:
        query: Search query
        top_k: Number of results

    Returns:
        Search results with context
    """
    retriever = get_knowledge_retriever()
    return retriever.search_with_context(query, top_k=top_k)


# Initialize on module load (optional, can lazy init)
def initialize_rag():
    """Manually initialize RAG"""
    retriever = get_knowledge_retriever()
    retriever.initialize(force_rebuild=True)
