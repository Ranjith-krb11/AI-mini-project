from core.llm_setup import get_llm
from tools.retrieval import retrieve_context

def generate_quiz(user_request):
    """Generates a formatted multiple-choice quiz based on the syllabus."""
    
    context = retrieve_context(user_request, n_results=5)
    
    if not context:
        return '{"type": "error", "message": "I couldn\'t find enough information in your notes to make a quiz about that. Try a different topic!"}'
        
    llm = get_llm()
    
    # --- THE BULLETPROOF PROMPT ---
    prompt = f"""
    You are an expert professor evaluating study notes to create a quiz. 
    
    Requested Topic: "{user_request}"
    
    UPLOADED NOTES CONTEXT:
    {context}
    
    STRICT INSTRUCTIONS:
    1. RELEVANCE CHECK FIRST: You must first read the 'UPLOADED NOTES CONTEXT'. Does it contain factual information about the Requested Topic ("{user_request}")?
    
    2. THE ESCAPE HATCH (Crucial): If the context is about a completely different subject (for example, if the context is about Java programming but the user asked for AI), you MUST NOT generate a quiz. You must abort and return ONLY this exact JSON:
    {{
      "type": "error",
      "message": "The retrieved notes do not contain information about the requested topic."
    }}
    
    3. QUIZ GENERATION: ONLY if the context is highly relevant to the Requested Topic, generate the quiz (default 3 questions unless specified). You MUST output ONLY valid JSON using this schema:
    {{
      "type": "quiz",
      "questions": [
        {{
          "question": "Question text?",
          "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
          "correct_answer": "A) Option 1",
          "reason": "This is correct because..."
        }}
      ]
    }}
    
    Remember: Output ONLY valid JSON. No markdown, no explanations outside the JSON.
    """
    
    try:
        response = llm.generate_content(prompt)
        text = response.text.strip()
        
        # Clean up markdown code blocks if the LLM still returns them
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
            
        if text.endswith("```"):
            text = text[:-3]
            
        return text.strip()
        
    except Exception as e:
        return f'{{"type": "error", "message": "An error occurred while generating the quiz: {str(e)}"}}'