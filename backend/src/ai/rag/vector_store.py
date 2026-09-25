"""
Vector Store - Store and search embeddings

Sử dụng:
    - Chroma (file-based, persistent)
    - Fallback: Simple numpy FAISS-like search
"""
from typing import List, Dict, Any, Optional
import numpy as np
from pathlib import Path
import json
import os


class VectorStore:
    """
    Simple vector store with cosine similarity search.
    Can use Chroma if available, otherwise simple numpy-based.
    """

    def __init__(
        self,
        persist_directory: str = None,
        collection_name: str = "knowledge"
    ):
        self.collection_name = collection_name
        self.embeddings = []
        self.metadata = []
        self.texts = []

        if persist_directory is None:
            base_dir = Path(__file__).parent.parent.parent.parent
            persist_directory = base_dir / "data" / "rag_storage"

        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Try to use Chroma
        self._chroma = None
        self._use_chroma = False
        self._try_chroma()

    def _try_chroma(self):
        """Try to initialize Chroma"""
        try:
            import chromadb
            from chromadb.config import Settings

            client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(anonymized_telemetry=False)
            )

            self._chroma = client.get_or_create_collection(self.collection_name)
            self._use_chroma = True
            print(f"Using Chroma vector store: {self.collection_name}")
        except ImportError:
            print("Chroma not available, using simple vector store")
            self._use_chroma = False

    def add(self, texts: List[str], embeddings: np.ndarray, metadata: List[Dict[str, Any]]):
        """Add documents to the store"""
        if self._use_chroma and self._chroma is not None:
            ids = [f"doc_{i}" for i in range(len(texts))]
            self._chroma.add(
                documents=texts,
                embeddings=embeddings.tolist(),
                metadatas=metadata,
                ids=ids
            )
        else:
            self.texts.extend(texts)
            self.embeddings.extend(embeddings)
            self.metadata.extend(metadata)

    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
        threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            threshold: Minimum similarity score

        Returns:
            List of results with text, metadata, and score
        """
        if self._use_chroma and self._chroma is not None:
            return self._search_chroma(query_embedding, k, threshold)
        else:
            return self._search_simple(query_embedding, k, threshold)

    def _search_chroma(
        self,
        query_embedding: np.ndarray,
        k: int,
        threshold: float
    ) -> List[Dict[str, Any]]:
        """Search using Chroma"""
        results = self._chroma.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=k
        )

        search_results = []
        if results and results.get("documents"):
            for i, doc in enumerate(results["documents"][0]):
                distance = results["distances"][0][i] if results.get("distances") else 1.0
                score = 1.0 - distance  # Convert distance to similarity

                if score >= threshold:
                    search_results.append({
                        "content": doc,
                        "score": float(score),
                        "source": results["metadatas"][0][i].get("source", "") if results.get("metadatas") else "",
                        "document": results["metadatas"][0][i].get("document", "") if results.get("metadatas") else "",
                        "section": results["metadatas"][0][i].get("section", "") if results.get("metadatas") else "",
                        "chunk_id": results["ids"][0][i] if results.get("ids") else "",
                    })

        return search_results

    def _search_simple(
        self,
        query_embedding: np.ndarray,
        k: int,
        threshold: float
    ) -> List[Dict[str, Any]]:
        """Simple numpy-based search with cosine similarity"""
        if not self.embeddings:
            return []

        embeddings_array = np.array(self.embeddings)

        # Compute cosine similarity
        query_norm = np.linalg.norm(query_embedding)
        if query_norm == 0:
            return []

        query_normalized = query_embedding / query_norm
        embeddings_normalized = embeddings_array / (
            np.linalg.norm(embeddings_array, axis=1, keepdims=True) + 1e-10
        )

        similarities = np.dot(embeddings_normalized, query_normalized)

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score >= threshold:
                results.append({
                    "content": self.texts[idx],
                    "score": score,
                    "source": self.metadata[idx].get("source", ""),
                    "document": self.metadata[idx].get("document", ""),
                    "section": self.metadata[idx].get("section", ""),
                    "chunk_id": self.metadata[idx].get("chunk_id", ""),
                })

        return results

    def persist(self):
        """Persist vector store to disk"""
        if not self._use_chroma:
            # Save simple index
            data = {
                "texts": self.texts,
                "embeddings": [e.tolist() if isinstance(e, np.ndarray) else e for e in self.embeddings],
                "metadata": self.metadata
            }
            path = self.persist_directory / f"{self.collection_name}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Persisted vector store to {path}")

    def load(self):
        """Load vector store from disk"""
        if not self._use_chroma:
            path = self.persist_directory / f"{self.collection_name}.json"
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.texts = data.get("texts", [])
                self.embeddings = [np.array(e) for e in data.get("embeddings", [])]
                self.metadata = data.get("metadata", [])
                print(f"Loaded {len(self.texts)} documents from {path}")


# Singleton instance
_vector_store = None


def get_vector_store() -> VectorStore:
    """Get singleton vector store"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
        # Try to load existing data
        _vector_store.load()
    return _vector_store
