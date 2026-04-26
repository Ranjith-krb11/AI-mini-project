import React from 'react';
import { FiCalendar, FiTarget } from 'react-icons/fi';

export const InteractiveRevisionPlan = ({ data }) => {
  if (!data || !data.days) return null;

  return (
    <div className="interactive-revision-plan">
      <div className="plan-header">
        <FiCalendar className="header-icon" />
        <h3 className="plan-title">{data.title || 'Revision Plan'}</h3>
      </div>
      
      <div className="timeline">
        {data.days.map((dayPlan, index) => (
          <div key={index} className="timeline-item">
            <div className="timeline-marker"></div>
            <div className="timeline-content">
              <h4 className="day-label">{dayPlan.day}</h4>
              
              <div className="day-details">
                <div className="day-topics">
                  <strong>Topics:</strong>
                  <div className="tags">
                    {dayPlan.topics.map((topic, tIdx) => (
                      <span key={tIdx} className="topic-tag">{topic}</span>
                    ))}
                  </div>
                </div>
                
                <div className="day-activities">
                  <FiTarget className="activity-icon" />
                  <span>{dayPlan.activities}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
