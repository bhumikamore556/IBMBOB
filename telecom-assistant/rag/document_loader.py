"""
Document loader for PDF files.
Extracts text content from uploaded telecom learning materials.
"""

import os
from typing import List, Dict, Any
from pathlib import Path

try:
    import pymupdf as fitz  # PyMuPDF >= 1.24
except ImportError:
    import fitz  # PyMuPDF < 1.24 fallback


def load_pdf(file_path: str) -> List[Dict[str, Any]]:
    """
    Load a PDF file and extract text page by page.

    Returns a list of dicts with keys:
        - page_content: str
        - metadata: dict (source, page)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Unsupported file type: {path.suffix}. Only PDF files are supported.")

    documents = []
    try:
        pdf_document = fitz.open(str(path))
    except Exception as exc:
        raise RuntimeError(f"Failed to open PDF: {exc}") from exc

    if len(pdf_document) == 0:
        raise ValueError("The PDF file is empty (zero pages).")

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        text = page.get_text("text")
        text = text.strip()
        if text:  # skip blank pages
            documents.append(
                {
                    "page_content": text,
                    "metadata": {
                        "source": path.name,
                        "page": page_num + 1,
                        "total_pages": len(pdf_document),
                    },
                }
            )

    pdf_document.close()

    if not documents:
        raise ValueError(
            "No text could be extracted from the PDF. "
            "The file may be scanned or image-based."
        )

    return documents


def load_pdf_from_bytes(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    """
    Load a PDF from bytes (e.g., Streamlit UploadedFile.read()).
    """
    documents = []
    try:
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise RuntimeError(f"Failed to open PDF: {exc}") from exc

    if len(pdf_document) == 0:
        raise ValueError("The PDF file is empty (zero pages).")

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        text = page.get_text("text").strip()
        if text:
            documents.append(
                {
                    "page_content": text,
                    "metadata": {
                        "source": filename,
                        "page": page_num + 1,
                        "total_pages": len(pdf_document),
                    },
                }
            )

    pdf_document.close()

    if not documents:
        raise ValueError(
            "No text could be extracted from the PDF. "
            "The file may be scanned or image-based."
        )

    return documents
