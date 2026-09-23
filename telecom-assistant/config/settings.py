"""
Configuration settings loaded from environment variables.
"""

import os
from dotenv import load_dotenv


class Settings:
    def __init__(self):
        # Reload .env each time a Settings instance is created so that
        # credentials added after the module was first imported are picked up.
        load_dotenv(override=True)

        # Groq credentials
        self.GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
        self.GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

        # HuggingFace token (optional — silences unauthenticated-request warnings)
        self.HF_TOKEN: str = os.getenv("HF_TOKEN", "")
        if self.HF_TOKEN:
            os.environ["HUGGING_FACE_HUB_TOKEN"] = self.HF_TOKEN
            os.environ["HF_TOKEN"] = self.HF_TOKEN

        # Embedding model
        self.EMBEDDING_MODEL: str = os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )

        # Document chunking
        self.CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
        self.CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))

        # Retrieval
        self.RETRIEVAL_TOP_K: int = int(os.getenv("RETRIEVAL_TOP_K", "4"))

        # Vector store path
        self.VECTOR_STORE_PATH: str = os.getenv(
            "VECTOR_STORE_PATH", "data/vectorstore"
        )

        # Documents path
        self.DOCUMENTS_PATH: str = os.getenv("DOCUMENTS_PATH", "data/documents")

        # Generation parameters
        self.MAX_NEW_TOKENS: int = int(os.getenv("MAX_NEW_TOKENS", "1024"))
        self.TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
        self.TOP_P: float = float(os.getenv("TOP_P", "0.9"))
        self.TOP_K: int = int(os.getenv("TOP_K", "50"))

    def validate(self) -> tuple[bool, list[str]]:
        """Validate required credentials are present."""
        errors = []
        if not self.GROQ_API_KEY:
            errors.append("GROQ_API_KEY is not set.")
        return len(errors) == 0, errors


settings = Settings()
