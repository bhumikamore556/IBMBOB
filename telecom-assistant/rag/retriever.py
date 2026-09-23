"""
Retriever: wraps the vector store query into a clean interface
used by the QA service.
"""

from typing import List, Dict, Any, Optional
from rag.vector_store import query_documents
from config.settings import settings


def retrieve(
    query: str,
    top_k: int = None,
    filter_source: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve the most semantically relevant document chunks for a query.

    Args:
        query: the user's question or search string
        top_k: number of chunks to return
        filter_source: optional filename to restrict retrieval

    Returns:
        List of chunk dicts: {page_content, metadata, distance}
    """
    top_k = top_k or settings.RETRIEVAL_TOP_K
    results = query_documents(query, top_k=top_k, filter_source=filter_source)
    return results


def format_context(chunks: List[Dict[str, Any]]) -> str:
    """
    Format retrieved chunks into a single context string for the LLM prompt.
    """
    if not chunks:
        return ""

    parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk["metadata"].get("source", "Unknown")
        page = chunk["metadata"].get("page", "?")
        parts.append(
            f"[Source {i}: {source}, Page {page}]\n{chunk['page_content']}"
        )
    return "\n\n---\n\n".join(parts)


def get_source_references(chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Extract unique source references from retrieved chunks.

    Returns a list of dicts: {source, page}
    """
    seen = set()
    refs = []
    for chunk in chunks:
        source = chunk["metadata"].get("source", "Unknown")
        page = chunk["metadata"].get("page", "?")
        key = f"{source}::page{page}"
        if key not in seen:
            seen.add(key)
            refs.append({"source": source, "page": str(page)})
    return refs
