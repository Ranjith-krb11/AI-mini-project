# AI Exam Revision Assistant

A decoupled, scalable web application featuring a modern React.js frontend and a FastAPI Python backend. This application allows users to upload PDF notes and interact with an AI agent to generate quizzes, flashcards, explanations, and day-by-day revision plans based *only* on the uploaded syllabus context.

## Prerequisites

Before running the project on a new device, ensure you have the following installed:
- **Python 3.9+** (For the FastAPI backend)
- **Node.js (v18+) and npm** (For the React frontend)
- A **Gemini API Key** from Google AI Studio.

---

## 1. Backend Setup (FastAPI)

The backend handles PDF ingestion, vector database storage (ChromaDB), and AI Agent processing.

1. **Clone the repository and navigate to the project root:**
   ```bash
   git clone <your-github-repo-url>
   cd AI-mini-project
   ```

2. **Create and activate a Python virtual environment:**
   - **Windows:**
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - **Mac/Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install the required Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your Environment Variables:**
   Create a `.env` file in the root folder of the project and add your Gemini API key:
   ```env
   GEMINI_API_KEY="your_actual_api_key_here"
   ```

5. **Start the FastAPI server:**
   ```bash
   uvicorn main:app --reload
   ```
   *The backend will now be running on `http://localhost:8000`.*

---

## 2. Frontend Setup (React/Vite)

The frontend provides a clean, responsive UI to interact with the backend services.

1. **Open a NEW terminal window** (keep the backend server running in the first one).
2. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

3. **Install Node dependencies:**
   ```bash
   npm install
   ```

4. **Start the Vite development server:**
   ```bash
   npm run dev
   ```
   *The frontend will now be running on `http://localhost:5173`. Open this URL in your browser to use the app!*

---

## Features

- **PDF Uploads:** Securely chunk and store your syllabus using local ChromaDB vector storage.
- **Interactive Quizzes:** Ask the AI to test your knowledge and get a clickable multiple-choice UI with instant correct/incorrect feedback.
- **Study Flashcards:** Generate a grid of click-to-flip flashcards to memorize key concepts.
- **Concept Explanations:** Get a structured breakdown of difficult concepts, complete with analogies and key takeaways.
- **Revision Planner:** Generate a day-by-day timeline schedule covering specific topics and study activities.