"""
Quiz Service: AI-powered quiz generation using Groq AI.
Generates multiple-choice telecom questions with answers and explanations.
"""

import json
import re
from typing import List, Dict, Any, Optional
from models.granite_model import generate_response
from rag.retriever import retrieve, format_context
from rag.vector_store import get_knowledge_base_info

QUIZ_PROMPT_TEMPLATE = """You are a telecommunications education expert creating a multiple-choice quiz.

{context_section}
Topic: {topic}
Difficulty: {difficulty}
Number of questions: {num_questions}

Generate exactly {num_questions} multiple-choice questions about {topic} at {difficulty} difficulty level.

IMPORTANT: Return ONLY valid JSON. No explanation, no markdown, no code fences. Just the JSON array.

Format:
[
  {{
    "question": "Question text here?",
    "options": {{
      "A": "First option",
      "B": "Second option",
      "C": "Third option",
      "D": "Fourth option"
    }},
    "correct_answer": "A",
    "explanation": "Brief explanation of why A is correct."
  }}
]

Difficulty guidelines:
- Easy: Basic definitions, simple concepts, introductory level
- Medium: Application of concepts, comparisons, intermediate level
- Hard: In-depth technical details, complex scenarios, advanced level

Generate the JSON array now:"""

CONTEXT_SECTION_TEMPLATE = """Use the following telecom learning material as the primary source:

{context}

"""


def generate_quiz(
    topic: str,
    num_questions: int = 5,
    difficulty: str = "Medium",
    use_documents: bool = True,
) -> List[Dict[str, Any]]:
    """
    Generate a multiple-choice quiz.

    Args:
        topic: Telecom topic (e.g., '5G', 'OFDM', 'LTE')
        num_questions: Number of questions to generate
        difficulty: 'Easy', 'Medium', or 'Hard'
        use_documents: Whether to use uploaded documents as context

    Returns:
        List of question dicts with question, options, correct_answer, explanation
    """
    if not topic or not topic.strip():
        raise ValueError("Quiz topic cannot be empty.")

    num_questions = max(1, min(num_questions, 20))  # clamp 1-20
    difficulty = difficulty.strip().capitalize()
    if difficulty not in ("Easy", "Medium", "Hard"):
        difficulty = "Medium"

    # Optionally retrieve document context
    context_section = ""
    kb_info = get_knowledge_base_info()
    if use_documents and kb_info["total_chunks"] > 0:
        chunks = retrieve(topic, top_k=6)
        if chunks:
            context = format_context(chunks)
            context_section = CONTEXT_SECTION_TEMPLATE.format(context=context)

    prompt = QUIZ_PROMPT_TEMPLATE.format(
        context_section=context_section,
        topic=topic.strip(),
        difficulty=difficulty,
        num_questions=num_questions,
    )

    raw_response = generate_response(prompt)
    questions = _parse_quiz_response(raw_response, num_questions)
    return questions


def _parse_quiz_response(
    raw: str,
    expected_count: int,
) -> List[Dict[str, Any]]:
    """
    Parse the model's JSON response into a list of question dicts.
    Handles common formatting issues.
    """
    # Strip markdown fences if present
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"```$", "", cleaned, flags=re.MULTILINE)
    cleaned = cleaned.strip()

    # Find JSON array bounds
    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(
            f"Model did not return valid JSON quiz data. Raw response:\n{raw[:500]}"
        )

    json_str = cleaned[start : end + 1]

    try:
        questions = json.loads(json_str)
    except json.JSONDecodeError as exc:
        # Try to repair common issues: trailing commas
        repaired = re.sub(r",\s*([}\]])", r"\1", json_str)
        try:
            questions = json.loads(repaired)
        except json.JSONDecodeError:
            raise ValueError(
                f"Failed to parse quiz JSON: {exc}\nRaw JSON:\n{json_str[:500]}"
            ) from exc

    if not isinstance(questions, list):
        raise ValueError("Quiz response is not a JSON array.")

    # Validate and normalise each question
    valid_questions = []
    for i, q in enumerate(questions):
        validated = _validate_question(q, i)
        if validated:
            valid_questions.append(validated)

    if not valid_questions:
        raise ValueError("No valid quiz questions could be parsed from the model response.")

    return valid_questions


def _validate_question(q: Any, index: int) -> Optional[Dict[str, Any]]:
    """Validate and normalise a single question dict."""
    if not isinstance(q, dict):
        return None

    question_text = q.get("question", "").strip()
    if not question_text:
        return None

    options = q.get("options", {})
    if not isinstance(options, dict):
        return None

    # Ensure all four options exist
    for key in ("A", "B", "C", "D"):
        if key not in options:
            return None
        options[key] = str(options[key]).strip()

    correct = str(q.get("correct_answer", "")).strip().upper()
    if correct not in ("A", "B", "C", "D"):
        correct = "A"  # default to A if invalid

    explanation = str(q.get("explanation", "")).strip()
    if not explanation:
        explanation = f"The correct answer is {correct}."

    return {
        "question": question_text,
        "options": options,
        "correct_answer": correct,
        "explanation": explanation,
    }


def score_quiz(
    questions: List[Dict[str, Any]],
    answers: Dict[int, str],
) -> Dict[str, Any]:
    """
    Score a completed quiz.

    Args:
        questions: list of question dicts
        answers: dict mapping question index (0-based) to chosen option letter

    Returns:
        Dict with score details and per-question results
    """
    total = len(questions)
    correct_count = 0
    results = []

    for i, q in enumerate(questions):
        user_answer = answers.get(i, "").strip().upper()
        correct = q["correct_answer"].upper()
        is_correct = user_answer == correct

        if is_correct:
            correct_count += 1

        results.append(
            {
                "question": q["question"],
                "user_answer": user_answer,
                "correct_answer": correct,
                "is_correct": is_correct,
                "explanation": q["explanation"],
                "options": q["options"],
            }
        )

    incorrect_topics = [
        r["question"] for r in results if not r["is_correct"]
    ]

    percentage = round((correct_count / total) * 100, 1) if total > 0 else 0.0

    return {
        "total": total,
        "correct": correct_count,
        "incorrect": total - correct_count,
        "percentage": percentage,
        "results": results,
        "incorrect_topics": incorrect_topics,
    }
