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
    2. Start with a direct, simple definition of the concept.
    3. Provide an everyday analogy to make the concept easier to understand.
    4. Highlight 2-3 key takeaways from the text using bullet points.
    5. Maintain an encouraging and supportive tone.
    
    UPLOADED NOTES CONTEXT:
    {context}
    """
    
    try:
        response = llm.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while explaining the concept: {str(e)}"