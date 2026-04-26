import React from 'react';
import { FiBookOpen, FiZap, FiCheckCircle } from 'react-icons/fi';

export const InteractiveExplanation = ({ data }) => {
  if (!data) return null;

  return (
    <div className="interactive-explanation">
      <div className="explanation-header">
        <FiBookOpen className="header-icon" />
        <h3 className="explanation-title">{data.concept}</h3>
      </div>
      
      <div className="explanation-section definition-section">
        <p>{data.definition}</p>
      </div>

      <div className="explanation-section analogy-section">
        <div className="section-heading">
          <FiZap className="section-icon analogy-icon" />
          <h4>Analogy</h4>
        </div>
        <p className="analogy-text">{data.analogy}</p>
      </div>

      <div className="explanation-section takeaways-section">
        <div className="section-heading">
          <FiCheckCircle className="section-icon takeaways-icon" />
          <h4>Key Takeaways</h4>
        </div>
        <ul className="takeaways-list">
          {data.takeaways.map((point, index) => (
            <li key={index}>{point}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};
