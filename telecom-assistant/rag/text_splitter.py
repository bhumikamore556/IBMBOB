"""
Text splitter: splits document pages into overlapping chunks
suitable for embedding and retrieval.
"""

from typing import List, Dict, Any
from config.settings import settings


def split_documents(
    documents: List[Dict[str, Any]],
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> List[Dict[str, Any]]:
    """
    Split a list of document dicts (page_content + metadata) into
    smaller overlapping chunks.

    Returns a list of chunk dicts with keys:
        - page_content: str
        - metadata: dict (source, page, chunk_index)
    """
    chunk_size = chunk_size or settings.CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    chunks = []
    for doc in documents:
        text = doc["page_content"]
        meta = doc["metadata"]
        doc_chunks = _split_text(text, chunk_size, chunk_overlap)
        for idx, chunk_text in enumerate(doc_chunks):
            chunks.append(
                {
                    "page_content": chunk_text,
                    "metadata": {
                        **meta,
                        "chunk_index": idx,
                    },
                }
            )
    return chunks


def _split_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """
    Simple character-based recursive splitter.
    Tries to split on paragraph boundaries first, then sentences, then characters.
    """
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    chunks = []
    separators = ["\n\n", "\n", ". ", " ", ""]
    _recursive_split(text, chunk_size, chunk_overlap, separators, chunks)
    return [c for c in chunks if c.strip()]


def _recursive_split(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
    separators: List[str],
    result: List[str],
) -> None:
    """Recursively split text using separators in order of preference."""
    if len(text) <= chunk_size:
        if text.strip():
            result.append(text.strip())
        return

    separator = ""
    for sep in separators:
        if sep == "" or sep in text:
            separator = sep
            break

    if separator == "":
        # Force-split by characters
        start = 0
        while start < len(text):
            end = start + chunk_size
            result.append(text[start:end].strip())
            start += chunk_size - chunk_overlap
        return

    parts = text.split(separator)
    current_chunk = ""

    for part in parts:
        candidate = (current_chunk + separator + part).strip() if current_chunk else part.strip()
        if len(candidate) <= chunk_size:
            current_chunk = candidate
        else:
            if current_chunk.strip():
                result.append(current_chunk.strip())
            # If the part itself is bigger than chunk_size, recurse
            if len(part) > chunk_size:
                _recursive_split(part, chunk_size, chunk_overlap, separators[1:], result)
                current_chunk = ""
            else:
                current_chunk = part.strip()

    if current_chunk.strip():
        result.append(current_chunk.strip())
