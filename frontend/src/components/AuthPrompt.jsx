import React from 'react';
import { X, LogIn, UserPlus } from 'lucide-react';
import './AuthPrompt.css';

const AuthPrompt = ({ isOpen, onClose, onLogin, onRegister }) => {
  if (!isOpen) return null;

  return (
    <div className="auth-prompt-overlay">
      <div className="auth-prompt-modal">
        <div className="auth-prompt-header">
          <h3>Authentication Required</h3>
          <button onClick={onClose} className="close-btn">
            <X size={20} />
          </button>
        </div>
        
        <div className="auth-prompt-content">
          <div className="auth-icon">
            <UserPlus size={48} />
          </div>
          
          <h4>Login to Continue</h4>
          <p>You need to be logged in to reserve a property. Please login or create an account to continue.</p>
          
          <div className="auth-actions">
            <button onClick={onLogin} className="btn-login">
              <LogIn size={16} />
              Login
            </button>
            <button onClick={onRegister} className="btn-register">
              <UserPlus size={16} />
              Create Account
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthPrompt;
