from typing import Optional, Tuple, List, Dict, Any
from core.llm_setup import get_llm
from tools.retrieval import retrieve_context_with_citations


def generate_flashcards(
    user_request: str,
    user_id: Optional[int] = None
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Generates a set of flashcards based on context, returning strict JSON and citations.
    """
    context, citations = retrieve_context_with_citations(user_request, user_id=user_id, n_results=5)
    llm = get_llm()

    context_prompt = f"UPLOADED NOTES CONTEXT:\n{context}" if context else "Generate flashcards using standard academic knowledge for this topic."

    prompt = f"""
    You are an expert study assistant. Create a set of flashcards for: "{user_request}"

    {context_prompt}

    Instructions:
    1. Generate 5 flashcards (or the number requested by the user).
    2. Output ONLY valid JSON matching this schema:
    {{
      "type": "flashcards",
      "cards": [
        {{
          "front": "Key Term, Question, or Concept",
          "back": "Concise, memorable definition or answer."
        }}
      ]
    }}
    3. Do NOT output markdown code blocks. Output ONLY raw JSON.
    """

    try:
        response = llm.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip(), citations
    except Exception as e:
        return f'{{"type": "error", "message": "An error occurred while generating flashcards: {str(e)}"}}', citations