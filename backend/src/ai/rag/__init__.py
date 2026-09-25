"""
RAG - Retrieval Augmented Generation Module

Cung cấp knowledge retrieval cho AI agents.

CHỈ dùng cho KNOWLEDGE - KHÔNG dùng cho realtime data.

Kiến trúc:
    Documents → Loader → Chunker → Embeddings → VectorStore → Retriever
"""
from src.ai.rag.retriever import KnowledgeRetriever, search_knowledge

__all__ = [
    "KnowledgeRetriever",
    "search_knowledge",
]
