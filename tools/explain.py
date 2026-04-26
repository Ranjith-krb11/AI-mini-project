from core.llm_setup import get_llm
from tools.retrieval import retrieve_context

def explain_concept(user_request):
    """Explains a complex concept using simple terms and analogies."""
    
    context = retrieve_context(user_request, n_results=3)
    
    if not context:
        return "I cannot find any information about that concept in the uploaded syllabus."
        
    llm = get_llm()
    
    prompt = f"""
    You are a friendly, expert tutor. The user needs help understanding a concept: "{user_request}"
    
    Strict Rules:
    1. Base your explanation ONLY on the provided context.
    2. You MUST output ONLY valid JSON without any markdown formatting or code blocks (no ```json).
    3. JSON Structure: Your response must strictly follow this JSON schema:
    {{
      "type": "explanation",
      "concept": "Name of the Concept",
      "definition": "Direct, simple definition of the concept.",
      "analogy": "Provide an everyday analogy to make it easier to understand.",
      "takeaways": [
        "Key takeaway 1",
        "Key takeaway 2",
        "Key takeaway 3"
      ]
    }}
    
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
        return text.strip()
    except Exception as e:
        return f'{{"type": "error", "message": "An error occurred while explaining the concept: {str(e)}"}}'