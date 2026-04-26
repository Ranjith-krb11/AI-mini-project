from core.llm_setup import get_llm
from tools.retrieval import retrieve_context

def generate_quiz(user_request):
    """Generates a formatted multiple-choice quiz based on the syllabus."""
    
    # 1. Fetch relevant notes (Increased to 5 chunks to support larger quizzes)
    context = retrieve_context(user_request, n_results=5)
    
    if not context:
        return "I couldn't find enough information in your notes to make a quiz about that. Try a different topic!"
        
    # 2. Initialize the AI
    llm = get_llm()
    
    # 3. The upgraded Quiz Prompt
    prompt = f"""
    You are an expert professor. Create a multiple-choice quiz based on this user request: "{user_request}"
    
    Strict Rules:
    1. Quantity: Read the user's request carefully. If they ask for a specific number of questions, generate exactly that many. Default to 3 questions.
    2. Formatting: You MUST output ONLY valid JSON without any markdown formatting or code blocks (no ```json). 
    3. JSON Structure: Your response must strictly follow this JSON schema:
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
    4. Accuracy: ONLY use the information found in the provided context. Do not make up facts.
    
    UPLOADED NOTES CONTEXT:
    {context}
    """
    
    # 4. Generate the quiz
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
        return f'{{"type": "error", "message": "An error occurred while generating the quiz: {str(e)}"}}'