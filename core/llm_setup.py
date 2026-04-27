import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from the .env file
load_dotenv()

# Configure the Groq API
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")

# Initialize the standard Groq client
client = Groq(api_key=api_key)

class GroqWrapper:
    """
    A wrapper class to make Groq's API mimic Google Gemini's syntax.
    This dynamically handles both single string prompts and lists of prompts (system + user).
    """
    def __init__(self, groq_client, model_name="llama-3.3-70b-versatile"):
        self.client = groq_client
        self.model_name = model_name
        
    def generate_content(self, prompt):
        messages = []
        
        # If the tool sends a list (e.g., in agent.py: [system_instruction, user_prompt])
        if isinstance(prompt, list) and len(prompt) == 2:
            messages.append({"role": "system", "content": str(prompt[0])})
            messages.append({"role": "user", "content": str(prompt[1])})
        # If the tool sends a single string (e.g., in quiz.py or flashcards.py)
        else:
            messages.append({"role": "user", "content": str(prompt)})

        # Make the call to Groq
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.2 # Lower temperature helps keep RAG output accurate and grounded
        )
        
        response_text = completion.choices[0].message.content
        
        # Create a mock response object that has a .text property, just like Gemini
        class MockGeminiResponse:
            def __init__(self, text):
                self.text = text
                
        return MockGeminiResponse(response_text)

def get_llm():
    """Returns the wrapped Groq model, applicable for all tools."""
    return GroqWrapper(client)