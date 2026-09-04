import React, { useState, useEffect, useRef, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import { useAuth } from '../context/AuthContext';
import {
  sendChatMessage,
  fetchConversations,
  fetchConversation,
  createConversation,
  deleteConversation,
} from '../services/api';
import { FiSend, FiUser, FiCpu, FiPlus, FiTrash2, FiMessageSquare, FiBookOpen } from 'react-icons/fi';
import { InteractiveQuiz } from './InteractiveQuiz';
import { InteractiveFlashcards } from './InteractiveFlashcards';
import { InteractiveExplanation } from './InteractiveExplanation';
import { InteractiveRevisionPlan } from './InteractiveRevisionPlan';

export const ChatInterface = () => {
  const { token, isAuthenticated } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [activeConvId, setActiveConvId] = useState(null);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! Upload your study notes or syllabus on the left, then ask me to explain concepts, generate quizzes, create flashcards, or answer specific questions with source citations.',
      sources: []
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [showHistorySidebar, setShowHistorySidebar] = useState(true);
  const messagesEndRef = useRef(null);

  // Load conversation list when authenticated
  const loadConversations = useCallback(async () => {
    if (!isAuthenticated) {
      setConversations([]);
      return;
    }
    try {
      const data = await fetchConversations(token);
      setConversations(data || []);
    } catch (err) {
      console.warn('Failed to load conversations:', err.message);
    }
  }, [isAuthenticated, token]);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // Load specific conversation messages
  const handleSelectConversation = async (convId) => {
    setActiveConvId(convId);
    setLoadingHistory(true);
    try {
      const data = await fetchConversation(convId, token);
      if (data && data.messages) {
        setMessages(data.messages);
      }
    } catch (err) {
      alert(`Could not load chat session: ${err.message}`);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleNewChat = async () => {
    setActiveConvId(null);
    setMessages([
      {
        role: 'assistant',
        content: 'New study session started! Ask me anything about your uploaded notes.',
        sources: []
      }
    ]);
  };

  const handleDeleteConversation = async (e, convId) => {
    e.stopPropagation();
    if (!window.confirm('Delete this conversation history?')) return;

    try {
      await deleteConversation(convId, token);
      setConversations((prev) => prev.filter((c) => c.id !== convId));
      if (activeConvId === convId) {
        handleNewChat();
      }
    } catch (err) {
      alert(`Failed to delete conversation: ${err.message}`);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userText = input.trim();
    const userMessage = { role: 'user', content: userText, sources: [] };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const data = await sendChatMessage(userText, token, activeConvId);

      // If a new conversation was created on the backend, update active ID and list
      if (data.conversation_id && (!activeConvId || activeConvId !== data.conversation_id)) {
        setActiveConvId(data.conversation_id);
        loadConversations();
      }

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.response,
          sources: data.sources || []
        }
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Error: ${error.message}`,
          sources: []
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessageContent = (msg) => {
    if (msg.role === 'assistant') {
      try {
        const parsed = typeof msg.content === 'string' && msg.content.trim().startsWith('{')
          ? JSON.parse(msg.content)
          : null;

        if (parsed) {
          if (parsed.type === 'quiz') {
            return <InteractiveQuiz quizData={parsed} />;
          }
          if (parsed.type === 'flashcards') {
            return <InteractiveFlashcards flashcardData={parsed} />;
          }
          if (parsed.type === 'explanation') {
            return <InteractiveExplanation data={parsed} />;
          }
          if (parsed.type === 'revision_plan') {
            return <InteractiveRevisionPlan data={parsed} />;
          }
          if (parsed.type === 'error') {
            return <div className="alert error-alert">{parsed.message}</div>;
          }
        }
      } catch (e) {
        // Fallback to markdown
      }
    }
    return <ReactMarkdown>{msg.content}</ReactMarkdown>;
  };

  return (
    <div className="component-card chat-interface-wrapper">
      <div className="chat-layout">
        {/* Conversation History Sidebar */}
        {isAuthenticated && (
          <aside className={`chat-history-sidebar ${showHistorySidebar ? 'open' : 'collapsed'}`}>
            <div className="history-sidebar-header">
              <button className="new-chat-btn" onClick={handleNewChat}>
                <FiPlus /> New Session
              </button>
            </div>

            <div className="history-list">
              {conversations.length === 0 ? (
                <div className="history-empty">No past sessions</div>
              ) : (
                conversations.map((conv) => (
                  <div
                    key={conv.id}
                    className={`history-item ${activeConvId === conv.id ? 'active' : ''}`}
                    onClick={() => handleSelectConversation(conv.id)}
                  >
                    <FiMessageSquare className="history-icon" />
                    <span className="history-title" title={conv.title}>
                      {conv.title}
                    </span>
                    <button
                      className="history-delete-btn"
                      onClick={(e) => handleDeleteConversation(e, conv.id)}
                      title="Delete session"
                    >
                      <FiTrash2 />
                    </button>
                  </div>
                ))
              )}
            </div>
          </aside>
        )}

        {/* Main Chat Area */}
        <div className="chat-main-area">
          <div className="chat-area-header">
            <h2 className="section-title">2. Study & Revision Session</h2>
            {isAuthenticated && (
              <button
                className="toggle-history-btn"
                onClick={() => setShowHistorySidebar((prev) => !prev)}
                title="Toggle conversation history"
              >
                {showHistorySidebar ? '◀ Hide History' : '▶ Chat History'}
              </button>
            )}
          </div>

          <div className="chat-window">
            <div className="messages-container">
              {loadingHistory ? (
                <div className="chat-loading-history">Loading session history...</div>
              ) : (
                messages.map((msg, idx) => (
                  <div key={idx} className={`message-row ${msg.role}`}>
                    <div className="avatar">
                      {msg.role === 'user' ? <FiUser /> : <FiCpu />}
                    </div>
                    <div className="message-content-wrapper">
                      <div className={`message-bubble ${msg.role}`}>
                        {renderMessageContent(msg)}
                      </div>

                      {/* Source Citations */}
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="citations-container">
                          <div className="citations-header">
                            <FiBookOpen className="citation-icon" />
                            <span>Sources:</span>
                          </div>
                          <div className="citations-badges">
                            {msg.sources.map((src, sIdx) => (
                              <span key={sIdx} className="citation-pill" title={`Chunk: ${src.chunk_number || 0}`}>
                                📄 {src.source} — Page {src.page_number}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}

              {isLoading && (
                <div className="message-row assistant">
                  <div className="avatar"><FiCpu /></div>
                  <div className="message-bubble assistant typing">
                    <div className="dot"></div>
                    <div className="dot"></div>
                    <div className="dot"></div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <form className="chat-input-form" onSubmit={handleSubmit}>
              <input
                type="text"
                className="chat-input"
                placeholder="Ask a question, request a quiz, flashcards, summary, or revision plan..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={isLoading}
              />
              <button
                type="submit"
                className="btn icon-btn send-btn"
                disabled={!input.trim() || isLoading}
              >
                <FiSend />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};
