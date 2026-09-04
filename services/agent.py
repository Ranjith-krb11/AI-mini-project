from typing import Optional, List, Dict, Any, Tuple
from core.llm_setup import get_llm
from tools.retrieval import retrieve_context_with_citations
from tools.quiz import generate_quiz
from tools.flashcards import generate_flashcards
from tools.explain import explain_concept
from tools.revision_planner import generate_revision_plan


def run_agent(
    user_prompt: str,
    user_id: Optional[int] = None,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    LLM-powered tool-routing agent:
    - Incorporates chat history for conversational continuity
    - Routes intent to specialized study tools (quiz, flashcards, explain, revision_plan, retrieval, general)
    - Enforces user-isolated vector context
    - Returns: (response_text_or_json, source_citations)
    """
    llm = get_llm()

    # Format recent conversation history (last 4 turns) for context
    history_summary = ""
    if chat_history and len(chat_history) > 0:
        recent_turns = chat_history[-4:]
        history_lines = []
        for turn in recent_turns:
            role = "User" if turn.get("role") == "user" else "Assistant"
            content = str(turn.get("content", ""))[:150]
            history_lines.append(f"{role}: {content}")
        history_summary = "Recent Conversation Context:\n" + "\n".join(history_lines) + "\n\n"

    tool_selector_prompt = f"""
    You are an intelligent AI exam revision agent.

    {history_summary}Current User Request:
    {user_prompt}

    Available Tools:
    1. quiz -> Generate practice multiple-choice quiz questions
    2. flashcards -> Generate interactive revision flashcards
    3. explain -> Explain concepts, break down complex topics, or list key points/takeaways
    4. revision_plan -> Create day-by-day study schedules / revision plans
    5. retrieval -> Search and answer specific questions from uploaded notes
    6. general -> General academic conversation or greetings

    Reply with ONLY the tool name in lowercase:
    quiz / flashcards / explain / revision_plan / retrieval / general
    """

    try:
        decision = llm.generate_content(tool_selector_prompt).text.strip().lower()

        # 1. QUIZ GENERATION
        if "quiz" in decision:
            return generate_quiz(user_prompt, user_id=user_id)

        # 2. FLASHCARDS
        elif "flashcards" in decision or "flashcard" in decision:
            return generate_flashcards(user_prompt, user_id=user_id)

        # 3. EXPLAIN / SUMMARIZE / KEY POINTS
        elif "explain" in decision:
            return explain_concept(user_prompt, user_id=user_id)

        # 4. REVISION PLANNER
        elif "revision_plan" in decision or "plan" in decision or "schedule" in decision:
            return generate_revision_plan(user_prompt, user_id=user_id)

        # 5. RETRIEVAL / Q&A FROM UPLOADED NOTES
        elif "retrieval" in decision or "search" in decision or "note" in decision:
            # If follow up, augment search query with recent context
            search_query = user_prompt
            if history_summary and len(user_prompt.split()) < 5:
                search_query = f"{recent_turns[-1].get('content', '')} {user_prompt}"

            context, citations = retrieve_context_with_citations(search_query, user_id=user_id, n_results=4)

            if not context:
                # Fallback to general LLM response with no citations
                fallback_prompt = f"{history_summary}User: {user_prompt}"
                response = llm.generate_content(fallback_prompt)
                return response.text, []

            final_prompt = f"""
            You are a helpful academic study assistant. Answer the user's question accurately using the context from their uploaded notes.

            {history_summary}UPLOADED NOTES CONTEXT:
            {context}

            User Question: {user_prompt}

            Answer clearly and concisely. Reference specific points from the context where appropriate.
            """

            response = llm.generate_content(final_prompt)
            return response.text, citations

        # 6. GENERAL RESPONSE
        else:
            general_prompt = f"{history_summary}User Question: {user_prompt}"
            response = llm.generate_content(general_prompt)
            return response.text, []

    except Exception as e:
        return f"Error processing request: {str(e)}", []