from core.llm_setup import get_llm
from tools.retrieval import retrieve_context
from tools.quiz import generate_quiz
from tools.flashcards import generate_flashcards
from tools.explain import explain_concept
from tools.revision_planner import generate_revision_plan


def run_agent(user_prompt):
    """
    Advanced Agentic AI:
    Uses LLM to understand intent, choose tool,
    reason, and generate final answer.
    """

    llm = get_llm()

    tool_selector_prompt = f"""
    You are an intelligent AI agent.

    Available tools:
    1. quiz -> Generate quiz questions
    2. flashcards -> Generate flashcards
    3. explain -> Explain concepts simply
    4. revision_plan -> Create study schedules / revision plans
    5. retrieval -> Search uploaded notes
    6. general -> Normal response

    User Request:
    {user_prompt}

    Reply with only one word:
    quiz / flashcards / explain / revision_plan / retrieval / general
    """

    try:
        decision = llm.generate_content(tool_selector_prompt).text.strip().lower()

        # TOOL 1
        if "quiz" in decision:
            return generate_quiz(user_prompt)

        # TOOL 2
        elif "flashcards" in decision:
            return generate_flashcards(user_prompt)

        # TOOL 3
        elif "explain" in decision:
            return explain_concept(user_prompt)
        
        elif "revision_plan" in decision or "plan" in decision or "schedule" in decision:
            return generate_revision_plan(user_prompt)

        # TOOL 4
        elif "retrieval" in decision:
            context = retrieve_context(user_prompt)
        
            if not context:
                return "No notes found. Please upload notes first."

            final_prompt = f"""
            Answer using only this context:

            {context}

            Question: {user_prompt}
            """

            response = llm.generate_content(final_prompt)
            return response.text

        # TOOL 5
        else:
            response = llm.generate_content(user_prompt)
            return response.text

    except Exception as e:
        return f"Error: {str(e)}"