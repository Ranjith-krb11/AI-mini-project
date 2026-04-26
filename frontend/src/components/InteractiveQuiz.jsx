import React, { useState } from 'react';
import { FiCheckCircle, FiXCircle } from 'react-icons/fi';

export const InteractiveQuiz = ({ quizData }) => {
  // Store the user's selected answers. Key: question index, Value: selected option string
  const [answers, setAnswers] = useState({});

  const handleOptionSelect = (qIndex, option) => {
    // Only allow selection if an answer hasn't been chosen yet for this question
    if (answers[qIndex] !== undefined) return;
    
    setAnswers(prev => ({
      ...prev,
      [qIndex]: option
    }));
  };

  if (!quizData || !quizData.questions || quizData.questions.length === 0) {
    return <div className="alert error-alert">Invalid quiz format.</div>;
  }

  return (
    <div className="interactive-quiz">
      <h3 className="quiz-title">📝 Practice Quiz</h3>
      <div className="quiz-questions">
        {quizData.questions.map((q, qIndex) => {
          const selectedAnswer = answers[qIndex];
          const isAnswered = selectedAnswer !== undefined;
          const isCorrect = isAnswered && selectedAnswer === q.correct_answer;

          return (
            <div key={qIndex} className="quiz-question-card">
              <h4 className="question-text">{qIndex + 1}. {q.question}</h4>
              
              <div className="options-list">
                {q.options.map((option, oIndex) => {
                  let optionClass = "quiz-option";
                  
                  if (isAnswered) {
                    if (option === q.correct_answer) {
                      optionClass += " correct";
                    } else if (option === selectedAnswer) {
                      optionClass += " incorrect";
                    } else {
                      optionClass += " disabled";
                    }
                  }

                  return (
                    <button
                      key={oIndex}
                      className={optionClass}
                      onClick={() => handleOptionSelect(qIndex, option)}
                      disabled={isAnswered}
                    >
                      <span className="option-text">{option}</span>
                      {isAnswered && option === q.correct_answer && (
                        <FiCheckCircle className="option-icon correct-icon" />
                      )}
                      {isAnswered && option === selectedAnswer && option !== q.correct_answer && (
                        <FiXCircle className="option-icon incorrect-icon" />
                      )}
                    </button>
                  );
                })}
              </div>
              
              {isAnswered && (
                <div className={`quiz-feedback ${isCorrect ? 'correct-feedback' : 'incorrect-feedback'}`}>
                  <strong>{isCorrect ? 'Correct!' : 'Incorrect.'}</strong> {q.reason}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
