from typing import Optional, Tuple, List, Dict, Any
from core.llm_setup import get_llm
from tools.retrieval import retrieve_context_with_citations


def generate_revision_plan(
    user_request: str,
    user_id: Optional[int] = None
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Generates a day-by-day revision plan based on context, returning strict JSON and citations.
    """
    context, citations = retrieve_context_with_citations(user_request, user_id=user_id, n_results=5)
    llm = get_llm()

    context_prompt = f"UPLOADED NOTES CONTEXT:\n{context}" if context else "Create a revision plan based on standard curriculum for this topic."

    prompt = f"""
    You are an expert study planner. Create a day-by-day revision plan for: "{user_request}"

    {context_prompt}

    Instructions:
    1. Organize the material into daily study goals and active recall activities.
    2. Default to 3 days if no duration is specified.
    3. Output ONLY valid JSON matching this schema:
    {{
      "type": "revision_plan",
      "title": "Custom Study & Revision Plan",
      "days": [
        {{
          "day": "Day 1",
          "topics": ["Topic A", "Topic B"],
          "activities": "Review chapter summary, practice 5 flashcards, and solve sample questions."
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
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip(), citations
    except Exception as e:
        return f'{{"type": "error", "message": "An error occurred while generating the revision plan: {str(e)}"}}', citations
