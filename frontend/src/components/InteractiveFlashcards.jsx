import React, { useState } from 'react';
import { FiRefreshCcw } from 'react-icons/fi';

export const InteractiveFlashcards = ({ flashcardData }) => {
  // Store an array of booleans indicating if a card is flipped
  const [flippedCards, setFlippedCards] = useState(
    new Array(flashcardData.cards?.length || 0).fill(false)
  );

  const handleFlip = (index) => {
    setFlippedCards(prev => {
      const newFlipped = [...prev];
      newFlipped[index] = !newFlipped[index];
      return newFlipped;
    });
  };

  if (!flashcardData || !flashcardData.cards || flashcardData.cards.length === 0) {
    return <div className="alert error-alert">Invalid flashcards format.</div>;
  }

  return (
    <div className="interactive-flashcards">
      <h3 className="flashcards-title">🗂️ Study Flashcards</h3>
      <div className="flashcards-grid">
        {flashcardData.cards.map((card, index) => (
          <div 
            key={index} 
            className={`flashcard-container ${flippedCards[index] ? 'flipped' : ''}`}
            onClick={() => handleFlip(index)}
          >
            <div className="flashcard-inner">
              <div className="flashcard-front">
                <span className="card-label">Concept</span>
                <h4>{card.front}</h4>
                <div className="flip-hint">
                  <FiRefreshCcw /> Click to flip
                </div>
              </div>
              <div className="flashcard-back">
                <span className="card-label">Definition</span>
                <p>{card.back}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
