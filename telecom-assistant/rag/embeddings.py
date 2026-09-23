"""
Embedding model wrapper.
Uses sentence-transformers (local, no API key required) to generate
dense vector embeddings for document chunks and queries.
"""

import warnings
from typing import List
from sentence_transformers import SentenceTransformer
from config.settings import settings

# Silence the HuggingFace Hub unauthenticated-request warning.
# The embedding model (all-MiniLM-L6-v2) is cached locally after first download
# and never needs an HF account to function.
warnings.filterwarnings(
    "ignore",
    message=".*unauthenticated.*",
    category=UserWarning,
)

# Module-level singleton so the model is loaded only once
_model: SentenceTransformer = None


def get_embedding_model() -> SentenceTransformer:
    """Return the cached SentenceTransformer model, loading it on first call."""
    global _model
    if _model is None:
        try:
            _model = SentenceTransformer(
                settings.EMBEDDING_MODEL,
                token=settings.HF_TOKEN or None,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load embedding model '{settings.EMBEDDING_MODEL}': {exc}"
            ) from exc
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Embed a list of strings and return a list of float vectors.
    """
    if not texts:
        return []
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embeddings.tolist()


def embed_query(query: str) -> List[float]:
    """
    Embed a single query string.
    """
    model = get_embedding_model()
    embedding = model.encode([query], show_progress_bar=False, convert_to_numpy=True)
    return embedding[0].tolist()
