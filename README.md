# Exam Revision Assistant

## Overview
This application helps students revise for exams by generating quizzes, flashcards, and explanations from uploaded syllabus PDFs.

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   streamlit run app.py
   ```

## Folder Structure
- `core/`: App-wide settings and configurations
- `database/`: Database connection and management
- `models/`: Data structures and validation
- `services/`: Core business logic
- `tools/`: Isolated functions for the agent
- `data/`: Local storage (ignored in version control)

## Environment Variables
Create a `.env` file with the following:
```
GEMINI_API_KEY="your_api_key_here"
```