from typing import Optional, Tuple, List, Dict, Any
from core.llm_setup import get_llm
from tools.retrieval import retrieve_context_with_citations


def explain_concept(
    user_request: str,
    user_id: Optional[int] = None
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Explains a concept or summarizes key points based on uploaded context,
    returning a structured JSON payload and citation metadata.
    """
    context, citations = retrieve_context_with_citations(user_request, user_id=user_id, n_results=4)
    llm = get_llm()

    if not context:
        prompt = f"""
        You are an expert tutor. The user is asking: "{user_request}".
        There are currently no uploaded notes matching this query.
        Provide a clear, educational explanation in valid JSON matching this schema:
        {{
          "type": "explanation",
          "concept": "{user_request}",
          "definition": "Direct, clear explanation of the topic.",
          "analogy": "A relatable analogy to clarify the concept.",
          "takeaways": [
            "Important point or takeaway 1",
            "Important point or takeaway 2",
            "Important point or takeaway 3"
          ]
        }}
        Output ONLY valid JSON. No markdown code blocks, no other text.
        """
    else:
        prompt = f"""
        You are a friendly, expert academic tutor. The user asks: "{user_request}"

        Instructions:
        1. Base your explanation, key points, and takeaways directly on the provided context below.
        2. Output ONLY valid JSON matching this schema:
        {{
          "type": "explanation",
          "concept": "Topic or Concept Name",
          "definition": "Direct, comprehensive explanation and important points from the context.",
          "analogy": "An everyday analogy to make the topic easy to remember.",
          "takeaways": [
            "Key takeaway / important point 1",
            "Key takeaway / important point 2",
            "Key takeaway / important point 3"
          ]
        }}
        3. Do NOT include markdown blocks like ```json. Output ONLY the raw JSON object.

        UPLOADED NOTES CONTEXT:
        {context}
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
        return f'{{"type": "error", "message": "An error occurred while explaining the concept: {str(e)}"}}', citations