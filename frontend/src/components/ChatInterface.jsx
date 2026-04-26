import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { sendChatMessage } from '../services/api';
import { FiSend, FiUser, FiCpu } from 'react-icons/fi';
import { InteractiveQuiz } from './InteractiveQuiz';
import { InteractiveFlashcards } from './InteractiveFlashcards';
import { InteractiveExplanation } from './InteractiveExplanation';
import { InteractiveRevisionPlan } from './InteractiveRevisionPlan';

export const ChatInterface = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! Upload your notes on the left, then ask me to quiz you or explain a topic.' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const data = await sendChatMessage(userMessage.content);
      setMessages((prev) => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      setMessages((prev) => [...prev, { role: 'assistant', content: `Error: ${error.message}` }]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessageContent = (msg) => {
    if (msg.role === 'assistant') {
      try {
        const parsed = JSON.parse(msg.content);
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
      } catch (e) {
        // Not a JSON string, fallback to markdown
      }
    }
    return <ReactMarkdown>{msg.content}</ReactMarkdown>;
  };

  return (
    <div className="component-card chat-interface">
      <h2 className="section-title">2. Study Session</h2>
      
      <div className="chat-window">
        <div className="messages-container">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message-row ${msg.role}`}>
              <div className="avatar">
                {msg.role === 'user' ? <FiUser /> : <FiCpu />}
              </div>
              <div className={`message-bubble ${msg.role}`}>
                {renderMessageContent(msg)}
              </div>
            </div>
          ))}
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
            placeholder="E.g., 'Create a 3-question multiple choice quiz on chapter 1'"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
          />
          <button type="submit" className="btn icon-btn send-btn" disabled={!input.trim() || isLoading}>
            <FiSend />
          </button>
        </form>
      </div>
    </div>
  );
};
