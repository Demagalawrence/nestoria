import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { Mail, Lock, ArrowRight, Building2, AlertCircle } from 'lucide-react';
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
      setError('Please enter both your email address and password.');
      return;
    }

    // Check if identifier is email or username
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const isEmail = emailRegex.test(identifier);

    // Validate email format if it looks like an email
    if (identifier.includes('@') && !isEmail) {
      setError('Please enter a valid email address (e.g., admin@example.com).');
      return;
    }

    // Validate password length
    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
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
          setError('The email and password combination you entered is incorrect. Please check your credentials and try again.');
        } else if (errorData.non_field_errors) {
          setError(errorData.non_field_errors.join(' '));
        } else if (errorData.username) {
          if (errorData.username.includes('does not exist')) {
            setError('No account found with this email address. Please check your email or sign up for a new account.');
          } else {
            setError(`Email: ${errorData.username.join(', ')}`);
          }
        } else if (errorData.password) {
          setError('Password: ' + errorData.password.join(', '));
        } else if (typeof errorData === 'object') {
          const errorMessages = Object.entries(errorData)
            .map(([field, messages]) => {
              const friendlyField = field === 'non_field_errors' ? 'Login' : field.charAt(0).toUpperCase() + field.slice(1);
              return `${friendlyField}: ${Array.isArray(messages) ? messages.join(', ') : messages}`;
            })
            .join('; ');
          setError(errorMessages);
        } else {
          setError(errorData.detail || errorData.error || 'Unable to login. Please check your credentials and try again.');
        }
      } else if (err.response?.status === 400) {
        setError('The email and password combination you entered is incorrect. Please double-check and try again.');
      } else if (err.response?.status === 401) {
        setError('Your session has expired. Please login again.');
      } else if (err.response?.status === 403) {
        setError('Access denied. You do not have permission to login.');
      } else if (err.response?.status >= 500) {
        setError('Server is currently experiencing issues. Please try again in a few minutes.');
      } else {
        setError('Unable to connect to the server. Please check your internet connection and try again.');
      }
    }
  };

  return (
    <div className="premium-auth-container">
      <div className="premium-auth-card animate-fade-in">
        <div className="premium-auth-header">
          <div className="premium-logo">
            <Building2 size={28} color="#ffffff" strokeWidth={2.5} />
          </div>
          <h2>Welcome back</h2>
          <p>Enter your details to access your account</p>
        </div>

        {error && (
          <div className="premium-error-message">
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="premium-auth-form">
          <div className="premium-input-group">
            <label>Email Address</label>
            <div className="premium-input-wrapper">
              <Mail className="premium-input-icon" size={20} />
              <input
                type="text"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder="name@example.com"
                required
              />
            </div>
          </div>

          <div className="premium-input-group">
            <label>Password</label>
            <div className="premium-input-wrapper">
              <Lock className="premium-input-icon" size={20} />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>
          </div>

          <button type="submit" className="premium-submit-btn">
            <span>Sign In</span>
            <ArrowRight size={18} />
          </button>
        </form>

        <div className="premium-auth-footer">
          <p>Don't have an account? <Link to="/register">Sign up for free</Link></p>
        </div>
      </div>
    </div>
  );
};

export default Login;
