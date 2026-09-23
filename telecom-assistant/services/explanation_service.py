"""
Explanation Service: Generates beginner-friendly explanations
of telecom concepts using Groq AI, optionally grounded in
uploaded documents.
"""

from typing import Dict, Any
from models.granite_model import generate_response
from rag.retriever import retrieve, format_context, get_source_references
from rag.vector_store import get_knowledge_base_info

EXPLANATION_PROMPT_TEMPLATE = """You are a telecommunications teacher explaining concepts to beginners.

{context_section}
Concept to explain: {concept}

Provide a clear, beginner-friendly explanation with the following structure:

## Simple Definition
[One or two sentences defining what {concept} is]

## How It Works
[Step-by-step or plain-language explanation of the mechanism]

## Real-World Example
[A concrete, relatable example that a student can visualize]

## Why It Is Important
[Why this concept matters in modern telecommunications]

## Key Points
- [Point 1]
- [Point 2]
- [Point 3]
- [Point 4]
- [Point 5]

Use simple language. Avoid unnecessary jargon. If technical terms are unavoidable, define them.

Explanation:"""

CONTEXT_SECTION_TEMPLATE = """Use the following information from uploaded telecom learning materials:

{context}

"""


def explain_concept(concept: str) -> Dict[str, Any]:
    """
    Generate a simplified explanation of a telecom concept.

    Returns:
        Dict with 'explanation', 'sources', 'from_documents'
    """
    if not concept or not concept.strip():
        return {
            "explanation": "Please enter a concept to explain.",
            "sources": [],
            "from_documents": False,
        }

    concept = concept.strip()

    # Try to retrieve relevant context from documents
    context_section = ""
    sources = []
    from_documents = False

    kb_info = get_knowledge_base_info()
    if kb_info["total_chunks"] > 0:
        chunks = retrieve(concept, top_k=4)
        if chunks:
            context = format_context(chunks)
            context_section = CONTEXT_SECTION_TEMPLATE.format(context=context)
            sources = get_source_references(chunks)
            from_documents = True

    prompt = EXPLANATION_PROMPT_TEMPLATE.format(
        context_section=context_section,
        concept=concept,
    )

    explanation = generate_response(prompt)

    return {
        "explanation": explanation,
        "sources": sources,
        "from_documents": from_documents,
    }
