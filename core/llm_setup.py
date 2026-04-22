import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Configure the Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=api_key)

def get_llm():
    """Returns the Gemini 3 Flash model, optimized for fast text tasks."""
    return genai.GenerativeModel('gemini-3-flash-preview')