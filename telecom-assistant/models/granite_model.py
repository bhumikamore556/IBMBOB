"""
Groq model integration.
Provides a single reusable generate_response() function.
"""

from config.settings import settings
from groq import Groq

# Lazy initialization
_client = None


def _get_client():
    """Initialize and return the Groq client."""
    global _client

    if _client is not None:
        return _client

    valid, errors = settings.validate()

    if not valid:
        raise RuntimeError(
            "Groq credentials are not configured.\n"
            + "\n".join(f"  - {e}" for e in errors)
        )

    try:
        from groq import Groq

        _client = Groq(
            api_key=settings.GROQ_API_KEY
        )

        return _client

    except ImportError as exc:
        raise ImportError(
            "groq package is not installed. "
            "Run: pip install groq"
        ) from exc

    except Exception as exc:
        raise RuntimeError(
            f"Failed to initialize Groq model: {exc}"
        ) from exc


def generate_response(prompt: str, context: str = "") -> str:
    """
    Generate a response from Groq.

    Args:
        prompt: Full prompt sent to the model.
        context: Optional context string.

    Returns:
        Generated text.
    """

    client = _get_client()

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=settings.MAX_NEW_TOKENS,
            temperature=settings.TEMPERATURE,
            top_p=settings.TOP_P,
        )

        return response.choices[0].message.content.strip()

    except Exception as exc:
        raise RuntimeError(
            f"Groq generation failed: {exc}"
        ) from exc


def is_configured() -> bool:
    """Return True if Groq credentials are configured."""
    valid, _ = settings.validate()
    return valid


def reset_model() -> None:
    """Reset the cached Groq client."""
    global _client
    _client = None