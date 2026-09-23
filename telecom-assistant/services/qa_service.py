"""
QA Service: RAG-based question answering.
Retrieves relevant context from the vector store and
passes it to Groq AI for answer generation.
"""

from typing import Dict, Any, List
from rag.retriever import retrieve, format_context, get_source_references
from rag.vector_store import get_knowledge_base_info
from models.granite_model import generate_response

RAG_PROMPT_TEMPLATE = """You are an AI assistant specialized in telecommunications education.
Answer the student's question using the provided context from telecom learning materials.

Context:
{context}

Student Question:
{question}

Instructions:
- Use the provided context whenever relevant.
- Explain technical concepts in clear, simple language suitable for students.
- Do not invent information that is not supported by the context.
- If the context does not contain enough information, clearly state that.
- Use examples where helpful.
- Structure the answer with bullet points or short paragraphs when appropriate.
- Be concise but thorough.

Answer:"""

NO_CONTEXT_RESPONSE = (
    "I could not find enough information about this topic in the uploaded telecom "
    "learning materials. Please upload relevant material or ask a question related "
    "to the available content."
)


def answer_question(
    question: str,
    top_k: int = None,
) -> Dict[str, Any]:
    """
    Answer a telecom question using RAG.

    Returns a dict with:
        - answer: str
        - sources: list of {source, page}
        - chunks_used: int
        - from_documents: bool
    """
    if not question or not question.strip():
        return {
            "answer": "Please enter a question.",
            "sources": [],
            "chunks_used": 0,
            "from_documents": False,
        }

    # Check if we have any documents
    kb_info = get_knowledge_base_info()
    if kb_info["total_chunks"] == 0:
        return {
            "answer": NO_CONTEXT_RESPONSE,
            "sources": [],
            "chunks_used": 0,
            "from_documents": False,
        }

    # Retrieve relevant chunks
    chunks = retrieve(question, top_k=top_k)

    if not chunks:
        return {
            "answer": NO_CONTEXT_RESPONSE,
            "sources": [],
            "chunks_used": 0,
            "from_documents": False,
        }

    # Format context
    context = format_context(chunks)
    sources = get_source_references(chunks)

    # Build RAG prompt
    prompt = RAG_PROMPT_TEMPLATE.format(
        context=context,
        question=question.strip(),
    )

    # Generate answer
    answer = generate_response(prompt)

    return {
        "answer": answer,
        "sources": sources,
        "chunks_used": len(chunks),
        "from_documents": True,
    }


def answer_with_chat_history(
    question: str,
    chat_history: List[Dict[str, str]],
    top_k: int = None,
) -> Dict[str, Any]:
    """
    Answer a question with awareness of previous conversation turns.

    chat_history: list of {'role': 'user'|'assistant', 'content': str}
    """
    if not question or not question.strip():
        return {
            "answer": "Please enter a question.",
            "sources": [],
            "chunks_used": 0,
            "from_documents": False,
        }

    kb_info = get_knowledge_base_info()
    has_documents = kb_info["total_chunks"] > 0

    chunks = []
    context = ""
    sources = []

    if has_documents:
        chunks = retrieve(question, top_k=top_k)
        if chunks:
            context = format_context(chunks)
            sources = get_source_references(chunks)

    # Build history string (last 4 turns max)
    history_str = ""
    if chat_history:
        recent = chat_history[-8:]  # last 4 user+assistant pairs
        for turn in recent:
            role = "Student" if turn["role"] == "user" else "Assistant"
            history_str += f"{role}: {turn['content']}\n"

    if context:
        prompt = f"""You are an AI assistant specialized in telecommunications education.
You have access to retrieved telecom learning materials. Use them to answer accurately.

Conversation History:
{history_str}
Retrieved Context:
{context}

Current Student Question:
{question.strip()}

Instructions:
- Use the context when it is relevant.
- Maintain conversation continuity.
- Explain concepts simply with examples.
- Do not invent unsupported facts.
- If context is insufficient, say so clearly.

Answer:"""
    else:
        prompt = f"""You are an AI assistant specialized in telecommunications education.

Conversation History:
{history_str}
Current Student Question:
{question.strip()}

Note: No learning materials are currently uploaded. Provide a general educational answer
about telecommunications. Clearly indicate this is a general answer, not document-based.

Answer:"""

    answer = generate_response(prompt)

    return {
        "answer": answer,
        "sources": sources,
        "chunks_used": len(chunks),
        "from_documents": len(chunks) > 0,
    }
