from core.llm_setup import get_llm
from tools.retrieval import retrieve_context

def generate_revision_plan(user_request):
    """Generates a day-by-day revision plan based on the uploaded notes."""
    
    context = retrieve_context(user_request, n_results=5)
    
    if not context:
        return "I couldn't find enough information in your notes to create a revision plan."
        
    llm = get_llm()
    
    prompt = f"""
    You are an expert study planner. Create a day-by-day revision plan based on this user request: "{user_request}"
    
    Strict Rules:
    1. Base the topics ONLY on the provided context.
    2. Read the user request to determine how many days the plan should cover. Default to 3 days if not specified.
    3. You MUST output ONLY valid JSON without any markdown formatting or code blocks (no ```json).
    4. JSON Structure: Your response must strictly follow this JSON schema:
    {{
      "type": "revision_plan",
      "title": "Your Custom Revision Plan",
      "days": [
        {{
          "day": "Day 1",
          "topics": ["Topic 1", "Topic 2"],
          "activities": "Read chapter 1, do 5 flashcards, etc."
        }}
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
        return f'{{"type": "error", "message": "An error occurred while generating the revision plan: {str(e)}"}}'
