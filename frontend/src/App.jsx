import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AuthModal } from './components/AuthModal';
import { FileUpload } from './components/FileUpload';
import { AdminPanel } from './components/AdminPanel';
import { ChatInterface } from './components/ChatInterface';
import './index.css';

function MainLayout() {
  const { user, isAuthenticated, logout, loading } = useAuth();
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState('login');

  const openAuth = (mode = 'login') => {
    setAuthMode(mode);
    setAuthModalOpen(true);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-brand">
          <h1>📚 AI Exam Revision Assistant</h1>
          <p>Upload your syllabus & notes to generate contextual Q&A, quizzes, flashcards, and personalized revision plans.</p>
        </div>

        <div className="header-auth">
          {loading ? (
            <div className="auth-loading-pill">Loading session...</div>
          ) : isAuthenticated ? (
            <div className="user-profile-badge">
              <div className="user-avatar" title={user.email}>
                {user.name.charAt(0).toUpperCase()}
              </div>
              <div className="user-info">
                <span className="user-name">{user.name}</span>
                <span className="user-email">{user.email}</span>
              </div>
              <button className="auth-btn logout-btn" onClick={logout}>
                Sign Out
              </button>
            </div>
          ) : (
            <div className="auth-actions">
              <button className="auth-btn signin-btn" onClick={() => openAuth('login')}>
                Sign In
              </button>
              <button className="auth-btn signup-btn" onClick={() => openAuth('register')}>
                Create Account
              </button>
            </div>
          )}
        </div>
      </header>

      {!isAuthenticated && !loading && (
        <div className="auth-notice-banner">
          <span>💡 <strong>Tip:</strong> Create an account or sign in to save your documents, isolate your study notes, and track conversation history across sessions.</span>
          <button className="banner-link-btn" onClick={() => openAuth('register')}>
            Sign Up Free →
          </button>
        </div>
      )}

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

      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        initialMode={authMode}
      />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <MainLayout />
    </AuthProvider>
  );
}

export default App;
