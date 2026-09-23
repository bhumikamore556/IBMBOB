"""
Vector store management using ChromaDB (persistent on disk).
Stores and retrieves document chunk embeddings.
"""

import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

from config.settings import settings
from rag.embeddings import embed_texts, embed_query

# Persistent ChromaDB client (singleton)
_client: chromadb.ClientAPI = None
_collection: chromadb.Collection = None
COLLECTION_NAME = "telecom_docs"


def _get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        persist_dir = Path(settings.VECTOR_STORE_PATH)
        persist_dir.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(
            path=str(persist_dir),
        )
    return _client


def get_collection() -> chromadb.Collection:
    """Get or create the telecom documents collection."""
    global _collection
    if _collection is None:
        client = _get_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_documents(chunks: List[Dict[str, Any]]) -> int:
    """
    Add document chunks to the vector store.

    Args:
        chunks: list of dicts with 'page_content' and 'metadata'

    Returns:
        Number of chunks added.
    """
    if not chunks:
        return 0

    collection = get_collection()

    texts = [c["page_content"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    # Generate unique IDs per chunk
    existing = collection.count()
    ids = [f"chunk_{existing + i}" for i in range(len(chunks))]

    # Generate embeddings
    embeddings = embed_texts(texts)

    # Serialize metadata values (ChromaDB requires str/int/float/bool)
    safe_metadatas = []
    for m in metadatas:
        safe_m = {k: (str(v) if not isinstance(v, (str, int, float, bool)) else v)
                  for k, v in m.items()}
        safe_metadatas.append(safe_m)

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=safe_metadatas,
    )

    return len(chunks)


def query_documents(
    query: str,
    top_k: int = None,
    filter_source: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Query the vector store for chunks similar to `query`.

    Returns a list of dicts with 'page_content', 'metadata', 'distance'.
    """
    top_k = top_k or settings.RETRIEVAL_TOP_K
    collection = get_collection()

    if collection.count() == 0:
        return []

    query_embedding = embed_query(query)

    where_filter = None
    if filter_source:
        where_filter = {"source": filter_source}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    docs = []
    if results and results["documents"]:
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            docs.append(
                {
                    "page_content": doc,
                    "metadata": meta,
                    "distance": dist,
                }
            )
    return docs


def get_knowledge_base_info() -> Dict[str, Any]:
    """Return stats about the current knowledge base."""
    collection = get_collection()
    count = collection.count()

    sources = set()
    if count > 0:
        # Retrieve all metadatas to collect unique sources
        results = collection.get(include=["metadatas"])
        for meta in results["metadatas"]:
            if "source" in meta:
                sources.add(meta["source"])

    return {
        "total_chunks": count,
        "documents": sorted(sources),
        "num_documents": len(sources),
    }


def delete_collection() -> None:
    """Clear the entire collection (for reset functionality)."""
    global _collection
    client = _get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    _collection = None
