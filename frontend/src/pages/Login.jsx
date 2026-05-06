import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import './Auth.css';

const Login = () => {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // Validate fields are not empty
    if (!identifier.trim() || !password.trim()) {
      setError('📝 Please enter both your email address and password.');
      return;
    }

    // Check if identifier is email or username
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const isEmail = emailRegex.test(identifier);

    // Validate email format if it looks like an email
    if (identifier.includes('@') && !isEmail) {
      setError('📧 Please enter a valid email address (e.g., admin@example.com).');
      return;
    }

    // Validate password length
    if (password.length < 6) {
      setError('🔑 Password must be at least 6 characters long.');
      return;
    }

    try {
      // Pass identifier (email or username) to login function
      const loginResult = await login(identifier, password);

      // Redirect based on user role
      if (loginResult.user?.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/properties');
      }
    } catch (err) {
      console.error('Login error:', err);
      const errorData = err.response?.data;

      if (errorData) {
        // Handle specific error messages with user-friendly text
        if (errorData.non_field_errors && errorData.non_field_errors.includes('Invalid credentials')) {
          setError('🔐 The email and password combination you entered is incorrect. Please check your credentials and try again.');
        } else if (errorData.non_field_errors) {
          setError(errorData.non_field_errors.join(' '));
        } else if (errorData.username) {
          if (errorData.username.includes('does not exist')) {
            setError('👤 No account found with this email address. Please check your email or sign up for a new account.');
          } else {
            setError(`📧 Email: ${errorData.username.join(', ')}`);
          }
        } else if (errorData.password) {
          setError('🔑 Password: ' + errorData.password.join(', '));
        } else if (typeof errorData === 'object') {
          const errorMessages = Object.entries(errorData)
            .map(([field, messages]) => {
              const friendlyField = field === 'non_field_errors' ? 'Login' : field.charAt(0).toUpperCase() + field.slice(1);
              return `${friendlyField}: ${Array.isArray(messages) ? messages.join(', ') : messages}`;
            })
            .join('; ');
          setError(errorMessages);
        } else {
          setError(errorData.detail || errorData.error || '❌ Unable to login. Please check your credentials and try again.');
        }
      } else if (err.response?.status === 400) {
        setError('🔐 The email and password combination you entered is incorrect. Please double-check and try again.');
      } else if (err.response?.status === 401) {
        setError('🔒 Your session has expired. Please login again.');
      } else if (err.response?.status === 403) {
        setError('🚫 Access denied. You do not have permission to login.');
      } else if (err.response?.status >= 500) {
        setError('🔧 Server is currently experiencing issues. Please try again in a few minutes.');
      } else {
        setError('❌ Unable to connect to the server. Please check your internet connection and try again.');
      }
    }
  };

  return (
    <div className="auth-container glassmorphism-bg">
      <div className="glassmorphism-card animate-fade-in">
        <div className="glass-header">
          <div className="logo-section">
            <div className="glass-logo">
              <svg viewBox="0 0 40 40" width="48" height="48" xmlns="http://www.w3.org/2000/svg" className="auth-logo-icon">
                <path d="M20 4L4 18h4v18h24V4z" fill="none" stroke="#3b82f6" strokeWidth="4" strokeLinejoin="round" />
                <path d="M16 36V22h-8v14h8z" fill="none" stroke="#3b82f6" strokeWidth="4" strokeLinejoin="round" />
              </svg>
            </div>
            <h2 className="glass-title">Welcome Back</h2>
          </div>
        </div>

        <p className="glass-subtitle">Sign in to continue to Nestoria</p>

        {error && <div className="glass-error">{error}</div>}

        <form onSubmit={handleSubmit} className="glass-form">
          <div className="glass-form-group">
            <label className="glass-label">Email Address</label>
            <div className="glass-input-wrapper">
              <input
                type="text"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder="Enter your email"
                className="glass-input"
                required
              />
              <div className="glass-input-icon">�</div>
            </div>
          </div>

          <div className="glass-form-group">
            <label className="glass-label">Password</label>
            <div className="glass-input-wrapper">
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="glass-input"
                required
              />
              <div className="glass-input-icon">🔑</div>
            </div>
          </div>

          <button type="submit" className="glass-submit-btn">
            <span className="glass-btn-text">Sign In</span>
            <div className="glass-btn-shine"></div>
          </button>
        </form>

        <div className="glass-footer">
          <span className="glass-footer-text">Don't have an account?</span>
          <Link to="/register" className="glass-link">Sign up</Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
