"""
Embeddings - Generate embeddings for text chunks

Sử dụng sentence-transformers (local, không cần API key).
Fallback: Simple TF-IDF nếu không cài được.
"""
from typing import List
import numpy as np


class EmbeddingsGenerator:
    """
    Generate embeddings for text chunks.
    Uses sentence-transformers if available, otherwise TF-IDF.
    """

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self.model = None
        self.embedding_dim = 384  # Default for MiniLM
        self.tfidf = None
        self._load_model()

    def _load_model(self):
        """Load embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            print(f"Loaded sentence-transformers model: {self.model_name}")
        except ImportError:
            print("sentence-transformers not available, using TF-IDF fallback")
            self.model = None
            self.tfidf = TFIDFVectorizer(self.embedding_dim)

    def embed(self, text: str) -> np.ndarray:
        """Generate embedding for single text"""
        if self.model is not None:
            return self.model.encode(text)
        else:
            return self._tfidf_embed(text)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts"""
        if self.model is not None:
            embeddings = self.model.encode(texts)
            return embeddings
        else:
            # Fit TF-IDF first if not fitted
            if self.tfidf and not self.tfidf.vocabulary:
                self.tfidf.fit(texts)
            return np.array([self._tfidf_embed(t) for t in texts])

    def _tfidf_embed(self, text: str) -> np.ndarray:
        """Simple TF-IDF fallback"""
        if self.tfidf and self.tfidf.vocabulary:
            return self.tfidf.transform([text])[0]
        # Simple word frequency vector
        words = text.lower().split()
        vector = np.zeros(self.embedding_dim)
        for i, word in enumerate(set(words)):
            if i < self.embedding_dim:
                vector[i] = words.count(word)
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector


class TFIDFVectorizer:
    """Simple TF-IDF vectorizer for local embeddings"""

    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.vocabulary = {}
        self.idf = {}

    def fit(self, texts: List[str]):
        """Build vocabulary from texts"""
        word_doc_freq = {}
        total_docs = len(texts)

        for text in texts:
            words = set(text.lower().split())
            for word in words:
                word_doc_freq[word] = word_doc_freq.get(word, 0) + 1

        # Build vocabulary (limit size)
        for i, word in enumerate(sorted(word_doc_freq.keys())):
            if i >= self.embedding_dim:
                break
            self.vocabulary[word] = i
            self.idf[word] = np.log(total_docs / (word_doc_freq[word] + 1))

    def transform(self, texts: List[str]) -> np.ndarray:
        """Transform texts to vectors"""
        vectors = []
        for text in texts:
            vector = np.zeros(self.embedding_dim)
            words = text.lower().split()
            word_count = {}
            for word in words:
                word_count[word] = word_count.get(word, 0) + 1

            for word, count in word_count.items():
                if word in self.vocabulary:
                    idx = self.vocabulary[word]
                    tf = count / len(words) if words else 0
                    vector[idx] = tf * self.idf.get(word, 1)

            # Normalize
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            vectors.append(vector)

        return np.array(vectors)


# Singleton instance
_embeddings_instance = None


def get_embeddings_generator() -> EmbeddingsGenerator:
    """Get singleton embeddings generator"""
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = EmbeddingsGenerator()
    return _embeddings_instance
