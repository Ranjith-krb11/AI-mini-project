from core.llm_setup import get_llm
from tools.retrieval import retrieve_context

def generate_flashcards(user_request):
    """Generates a set of flashcards based on the uploaded notes."""
    
    context = retrieve_context(user_request, n_results=4)
    
    if not context:
        return "I couldn't find enough information in your notes to make flashcards on that topic."
        
    llm = get_llm()
    
    prompt = f"""
    You are an expert study assistant. Create a set of flashcards based on this user request: "{user_request}"
    
    Strict Rules:
    1. Quantity: If the user asks for a specific number, generate exactly that many. Otherwise, default to 5.
    2. Formatting: You MUST output ONLY valid JSON without any markdown formatting or code blocks (no ```json).
    3. JSON Structure: Your response must strictly follow this JSON schema:
    {{
      "type": "flashcards",
      "cards": [
        {{
          "front": "Concept or Question",
          "back": "Definition or Answer"
        }}
      ]
    }}
    4. Accuracy: ONLY use the information found in the provided context.
    5. Brevity: Keep the "back" of the card concise and easy to memorize.
    
    UPLOADED NOTES CONTEXT:
    {context}
    """
    
    try:
        response = llm.generate_content(prompt)
        # Clean up markdown code blocks if the LLM still returns them
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
    except Exception as e:
        return f'{{"type": "error", "message": "An error occurred while generating flashcards: {str(e)}"}}'