import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export const AuthModal = ({ isOpen, onClose, initialMode = 'login' }) => {
  const [isLoginMode, setIsLoginMode] = useState(initialMode === 'login');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [formError, setFormError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { login, register, clearError } = useAuth();

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');
    setIsSubmitting(true);

    try {
      if (isLoginMode) {
        await login(email, password);
      } else {
        if (!name.trim()) {
          throw new Error('Please enter your full name');
        }
        if (password.length < 6) {
          throw new Error('Password must be at least 6 characters');
        }
        await register(name, email, password);
      }
      onClose();
    } catch (err) {
      setFormError(err.message || 'An error occurred during authentication.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const switchMode = (loginMode) => {
    setIsLoginMode(loginMode);
    setFormError('');
    clearError();
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="auth-modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="auth-modal-header">
          <div className="auth-tabs">
            <button
              type="button"
              className={`auth-tab ${isLoginMode ? 'active' : ''}`}
              onClick={() => switchMode(true)}
            >
              Sign In
            </button>
            <button
              type="button"
              className={`auth-tab ${!isLoginMode ? 'active' : ''}`}
              onClick={() => switchMode(false)}
            >
              Create Account
            </button>
          </div>
          <button className="modal-close-btn" onClick={onClose}>&times;</button>
        </div>

        <div className="auth-modal-body">
          <h2 className="auth-title">
            {isLoginMode ? 'Welcome back! 👋' : 'Get Started with AI Revision 🚀'}
          </h2>
          <p className="auth-subtitle">
            {isLoginMode
              ? 'Sign in to access your notes, quizzes, flashcards, and study history.'
              : 'Create a free account to upload syllabi and generate personalized study aids.'}
          </p>

          {formError && (
            <div className="auth-alert error">
              <span>⚠️ {formError}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            {!isLoginMode && (
              <div className="form-group">
                <label htmlFor="auth-name">Full Name</label>
                <input
                  id="auth-name"
                  type="text"
                  placeholder="Alex Morgan"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
            )}

            <div className="form-group">
              <label htmlFor="auth-email">Email Address</label>
              <input
                id="auth-email"
                type="email"
                placeholder="alex@university.edu"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="auth-password">Password</label>
              <input
                id="auth-password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
              />
            </div>

            <button
              type="submit"
              className="auth-submit-btn"
              disabled={isSubmitting}
            >
              {isSubmitting
                ? 'Processing...'
                : isLoginMode
                ? 'Sign In'
                : 'Create Account'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
