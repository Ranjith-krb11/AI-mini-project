from core.llm_setup import get_llm
from tools.retrieval import retrieve_context
from tools.quiz import generate_quiz
from tools.flashcards import generate_flashcards
from tools.explain import explain_concept

def run_agent(user_prompt):
    """Processes the user query and routes to the correct tool based on intent."""
    
    prompt_lower = user_prompt.lower()
    
    # --- ROUTE 1: The Quiz Tool ---
    if any(keyword in prompt_lower for keyword in ["quiz", "test me", "multiple choice"]):
        return generate_quiz(user_prompt)
        
    # --- ROUTE 2: The Flashcard Tool ---
    elif any(keyword in prompt_lower for keyword in ["flashcard", "flash card", "study cards"]):
        return generate_flashcards(user_prompt)
        
    # --- ROUTE 3: The Explainer Tool ---
    elif any(keyword in prompt_lower for keyword in ["explain", "how does", "what is", "help me understand", "analogy"]):
        return explain_concept(user_prompt)
    
    # --- ROUTE 4: Standard Q&A (Fallback) ---
    else:
        context = retrieve_context(user_prompt)
        
        if not context:
            return "I don't have any notes on that yet. Please upload a syllabus or notes PDF first!"

        llm = get_llm()
        
        system_instruction = f"""
        You are an expert Exam Revision Assistant. 
        Answer the user's question using ONLY the provided context from their notes.
        If the context does not contain the answer, say "I cannot find this information in the notes."
        
        UPLOADED NOTES CONTEXT:
        {context}
        """
        
        try:
            response = llm.generate_content([system_instruction, user_prompt])
            return response.text
        except Exception as e:
            return f"An error occurred: {str(e)}"