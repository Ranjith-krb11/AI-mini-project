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
    1. Quantity: If the user asks for a specific number (e.g., "5 flashcards"), generate exactly that many. Otherwise, default to 5.
    2. Formatting: You MUST format each flashcard exactly like this template:
    
       **Card 1**
       * **Front (Concept):** [Insert key term or question here]
       * **Back (Definition):** [Insert brief, clear definition or answer here]
            
       ---
       
    3. Accuracy: ONLY use the information found in the provided context.
    4. Brevity: Keep the "Back" of the card concise and easy to memorize.
    
    UPLOADED NOTES CONTEXT:
    {context}
    """
    
    try:
        response = llm.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while generating flashcards: {str(e)}"