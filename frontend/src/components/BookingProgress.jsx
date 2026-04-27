import React from 'react';
import { Check } from 'lucide-react';
import './BookingProgress.css';

const BookingProgress = ({ currentStep }) => {
  const steps = [
    { id: 1, label: 'Property' },
    { id: 2, label: 'Your Info' },
    { id: 3, label: 'Payment' },
    { id: 4, label: 'Confirm' }
  ];

  return (
    <div className="booking-progress-container">
      <div className="progress-track">
        {steps.map((step, index) => {
          const isCompleted = step.id < currentStep;
          const isActive = step.id === currentStep;
          const isPending = step.id > currentStep;

          return (
            <React.Fragment key={step.id}>
              {/* The Line before the circle */}
              {index > 0 && (
                <div 
                  className={`progress-line ${step.id <= currentStep ? 'completed-line' : 'pending-line'}`}
                ></div>
              )}
              
              {/* The Step Circle */}
              <div className="step-wrapper">
                <div 
                  className={`step-circle ${isCompleted || isActive ? 'completed' : 'pending'}`}
                >
                  {isCompleted ? (
                    <Check size={16} strokeWidth={3} className="check-icon" />
                  ) : (
                    <span className="step-number">{step.id}</span>
                  )}
                </div>
                <span className={`step-label ${isActive ? 'active-label' : ''}`}>
                  {step.label}
                </span>
              </div>
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};

export default BookingProgress;
