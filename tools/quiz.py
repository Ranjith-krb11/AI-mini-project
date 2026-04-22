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
    1. Quantity: Read the user's request carefully. If they ask for a specific number of questions (e.g., "5 questions"), generate exactly that many. If they do not specify a number, default to generating exactly 3 questions.
    2. Formatting: You MUST format the questions and options exactly like this template, with each option on a new line:
    
       **Question 1: [Insert Question Text Here]**
       A) [Option A text]
       B) [Option B text]
       C) [Option C text]
       D) [Option D text]
    3.Break: After question , each option must be on a new line. Do NOT put multiple options on the same line.
    4. Blank Lines: Ensure there is a blank line between the last option of a question and the start of the next question.
    5. Accuracy: ONLY use the information found in the provided context. Do not make up facts.
    6. Answer Key: At the VERY BOTTOM of your response, provide an "Answer Key" with the correct answers and a 1-sentence explanation for each.
    
    UPLOADED NOTES CONTEXT:
    {context}
    """
    
    # 4. Generate the quiz
    try:
        response = llm.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while generating the quiz: {str(e)}"