from google import genai
from core.config import settings

_client = None


def get_gemini_client():
    global _client
    if _client is None:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment or .env file")
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


class GeminiWrapper:
    """
    Wrapper so the rest of your application can continue using:
    
    llm.generate_content(prompt)
    
    and access:
    
    response.text
    """

    def __init__(self, client=None, model_name="gemini-3.5-flash"):
        self._client = client
        self.model_name = model_name

    @property
    def client(self):
        if self._client is None:
            self._client = get_gemini_client()
        return self._client

    def generate_content(self, prompt):
        # If your agent sends:
        # [system_instruction, user_prompt]
        if isinstance(prompt, list) and len(prompt) == 2:
            system_instruction = str(prompt[0])
            user_prompt = str(prompt[1])
            final_prompt = f"""
SYSTEM INSTRUCTION:
{system_instruction}

USER PROMPT:
{user_prompt}
"""
        else:
            final_prompt = str(prompt)

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=final_prompt
        )

        return response


def get_llm():
    """Returns Gemini model wrapper used by all tools."""
    return GeminiWrapper()