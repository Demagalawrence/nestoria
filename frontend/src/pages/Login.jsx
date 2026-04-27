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
        navigate('/');
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
    <div className="auth-container">
      <div className="auth-card glass-panel animate-fade-in">
        <h2 className="auth-title">Welcome Back</h2>
        <p className="auth-subtitle">Sign in to continue to Rent H&U</p>
        
        {error && <div className="auth-error">{error}</div>}
        
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>Email Address</label>
            <input 
              type="text" 
              value={identifier} 
              onChange={(e) => setIdentifier(e.target.value)} 
              placeholder="admin@example.com"
              required 
            />
            <small className="form-hint">💡 Use your email address (e.g., admin@example.com)</small>
          </div>
          <div className="form-group">
            <label>Password</label>
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              placeholder="Enter your password"
              required 
            />
            <small className="form-hint">🔑 Must be at least 6 characters</small>
          </div>
          
          <button type="submit" className="btn-primary auth-submit">Sign In</button>
        </form>
        
        <div className="auth-footer">
          Don't have an account? <Link to="/register">Sign up</Link>
        </div>
        
        <div className="demo-credentials">
          <h4>🔑 Demo Credentials</h4>
          <p><strong>Email:</strong> admin@example.com</p>
          <p><strong>Password:</strong> admin123</p>
        </div>
      </div>
    </div>
  );
};

export default Login;
