from core.llm_setup import get_llm
from tools.retrieval import retrieve_context
import json

def explain_concept(user_request):
    """Explains a complex concept using simple terms and analogies, returning strict JSON."""
    
    context = retrieve_context(user_request, n_results=3)
    
    # 1. Update the empty context check to return JSON instead of plain text
    if not context:
        return '{"type": "error", "message": "I cannot find any information about that concept in the uploaded syllabus."}'
        
    llm = get_llm()
    
    # 2. Update the prompt to handle both success (explanation) and failure (refusal) via JSON
    prompt = f"""
    You are a friendly, expert tutor. The user needs help understanding a concept: "{user_request}"
    
    Strict Rules:
    1. Base your explanation ONLY on the provided context.
    2. THE REFUSAL RULE: Read the context carefully. If the user's requested concept is NOT explicitly mentioned or discussed in the context below, you MUST NOT answer. Instead, output exactly this JSON: {{"type": "error", "message": "I cannot find information about this in your uploaded notes."}}
    3. You MUST output ONLY valid JSON without any markdown formatting or code blocks (no ```json).
    4. If the concept IS found in the context, your response must strictly follow this JSON schema:
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
        
        # Clean up any residual markdown the LLM might have stubbornly included
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        return text.strip()
        
    except Exception as e:
        # Ensure programmatic errors also return safely as JSON
        return f'{{"type": "error", "message": "An error occurred while explaining the concept: {str(e)}"}}'