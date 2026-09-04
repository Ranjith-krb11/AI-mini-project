from typing import Optional, Tuple, List, Dict, Any
from core.llm_setup import get_llm
from tools.retrieval import retrieve_context_with_citations


def generate_quiz(
    user_request: str,
    user_id: Optional[int] = None
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Generates a formatted multiple-choice quiz based on context,
    returning strict JSON and citation metadata.
    """
    context, citations = retrieve_context_with_citations(user_request, user_id=user_id, n_results=5)
    llm = get_llm()

    context_prompt = f"UPLOADED NOTES CONTEXT:\n{context}" if context else "No uploaded notes available. Generate a general academic quiz on the topic."

    prompt = f"""
    You are an expert professor preparing a multiple-choice practice quiz for a student.

    Requested Topic: "{user_request}"

    {context_prompt}

    Instructions:
    1. Generate 3 multiple choice questions (or the number requested by the user).
    2. If context is provided, base questions strictly on facts from the context.
    3. Output ONLY valid JSON matching this schema:
    {{
      "type": "quiz",
      "questions": [
        {{
          "question": "Question text?",
          "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
          "correct_answer": "A) Option 1",
          "reason": "Clear explanation of why this answer is correct."
        }}
      ]
    }}
    4. Do NOT output markdown code blocks. Output ONLY raw JSON.
    """

    try:
        response = llm.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip(), citations
    except Exception as e:
        return f'{{"type": "error", "message": "An error occurred while generating the quiz: {str(e)}"}}', citations