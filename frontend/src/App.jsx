import React from 'react';
import { FileUpload } from './components/FileUpload';
import { AdminPanel } from './components/AdminPanel';
import { ChatInterface } from './components/ChatInterface';
import './index.css';

function App() {
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>📚 Exam Revision Assistant</h1>
        <p>Upload your notes, and I'll help you study by explaining concepts, generating quizzes, or creating flashcards!</p>
      </header>

      <main className="app-main">
        <aside className="sidebar">
          <FileUpload />
          <div className="divider"></div>
          <AdminPanel />
        </aside>
        
        <section className="main-content">
          <ChatInterface />
        </section>
      </main>
    </div>
  );
}

export default App;
