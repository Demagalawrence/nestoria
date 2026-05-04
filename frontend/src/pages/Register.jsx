import React, { useState, useContext, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { Eye, EyeOff } from 'lucide-react';
import './Register.css';

// Load reCAPTCHA script
const loadReCaptcha = () => {
  return new Promise((resolve) => {
    if (window.grecaptcha) {
      resolve(window.grecaptcha);
      return;
    }
    
    const siteKey = import.meta.env.VITE_RECAPTCHA_SITE_KEY || '6LeIxAcTAAAAAJcZVRqyHh71UMIEbUjQbQxO4';
    const script = document.createElement('script');
    script.src = `https://www.google.com/recaptcha/api.js?render=${siteKey}`;
    script.async = true;
    script.defer = true;
    
    script.onload = () => {
      resolve(window.grecaptcha);
    };
    
    document.head.appendChild(script);
  });
};

const GoogleIcon = () => (
  <svg viewBox="0 0 24 24" width="18" height="18" xmlns="http://www.w3.org/2000/svg">
    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
  </svg>
);

const XIcon = () => (
  <svg viewBox="0 0 24 24" width="18" height="18" xmlns="http://www.w3.org/2000/svg">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" fill="currentColor" />
  </svg>
);

const LogoIcon = () => (
  <svg viewBox="0 0 40 40" width="48" height="48" xmlns="http://www.w3.org/2000/svg" className="auth-logo-icon">
    <path d="M20 4L4 18h4v18h24V18h4L20 4z" fill="none" stroke="#2563eb" strokeWidth="4" strokeLinejoin="round" />
    <path d="M16 36V22h8v14" fill="none" stroke="#2563eb" strokeWidth="4" strokeLinejoin="round" />
  </svg>
);

const Register = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    country_code: 'UG',
    phone_number: '',
    password: '',
    confirm_password: '',
    termsAccepted: false
  });

  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState(null);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [recaptchaToken, setRecaptchaToken] = useState('');
  const [isRecaptchaReady, setIsRecaptchaReady] = useState(false);
  const { register } = useContext(AuthContext);
  const navigate = useNavigate();

  // Initialize reCAPTCHA
  useEffect(() => {
    loadReCaptcha().then(() => {
      setIsRecaptchaReady(true);
    });
  }, []);

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setFormData({ ...formData, [e.target.name]: value });
  };

  const handleRecaptcha = () => {
    if (!isRecaptchaReady) return;
    
    const siteKey = import.meta.env.VITE_RECAPTCHA_SITE_KEY || '6LeIxAcTAAAAAJcZVRqyHh71UMIEbUjQbQxO4';
    
    window.grecaptcha.ready(() => {
      window.grecaptcha.execute(siteKey, { action: 'submit' })
        .then(token => {
          setRecaptchaToken(token);
        });
    });
  };

  // Execute reCAPTCHA on form submission
  useEffect(() => {
    handleRecaptcha();
  }, [isRecaptchaReady]);

  const handleSuccessModalOk = () => {
    setShowSuccessModal(false);
    navigate('/login');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!formData.name.trim() || !formData.email.trim() || !formData.password.trim()) {
      setError('📝 Please fill in all required fields.');
      return;
    }

    if (!formData.termsAccepted) {
      setError('✅ You must accept terms & conditions to register.');
      return;
    }

    if (!recaptchaToken) {
      setError('🤖 Please complete the reCAPTCHA verification.');
      handleRecaptcha();
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('📧 Please enter a valid email address.');
      return;
    }

    if (formData.password !== formData.confirm_password) {
      setError('🔐 Passwords do not match. Please check and try again.');
      return;
    }

    if (formData.password.length < 6) {
      setError('🔑 Password must be at least 6 characters long.');
      return;
    }

    const nameParts = formData.name.trim().split(' ');
    const firstName = nameParts[0];
    const lastName = nameParts.length > 1 ? nameParts.slice(1).join(' ') : 'User';

    let contactNumber = '';
    if (formData.phone_number.trim()) {
      const codeMap = { 'UG': '+256', 'US': '+1', 'UK': '+44' };
      contactNumber = `${codeMap[formData.country_code] || '+256'} ${formData.phone_number.trim()}`;
    }

    try {
      const submitData = new FormData();

      submitData.append('first_name', firstName);
      submitData.append('last_name', lastName);
      submitData.append('email', formData.email);
      submitData.append('username', formData.email);
      submitData.append('password', formData.password);
      submitData.append('confirm_password', formData.confirm_password);
      submitData.append('recaptcha_token', recaptchaToken);
      // submitData.append('user_type', 'user'); // Removed as API doesn't accept this field
      if (contactNumber) submitData.append('contact_number', contactNumber);

      await register(submitData);
      setShowSuccessModal(true);
    } catch (err) {
      console.error('Registration error:', err);
      const errorData = err.response?.data;
      if (errorData) {
        if (typeof errorData === 'object') {
          const errorMessages = Object.entries(errorData)
            .map(([field, messages]) => {
              const friendlyField = field === 'non_field_errors' ? 'Registration' : field.charAt(0).toUpperCase() + field.slice(1);
              return `${friendlyField}: ${Array.isArray(messages) ? messages.join(', ') : messages}`;
            })
            .join('; ');
          setError(errorMessages);
        } else {
          setError(errorData.detail || errorData.error || '❌ Registration failed. Please try again.');
        }
      } else {
        setError('❌ Unable to connect to server. Please check your internet connection and try again.');
      }
    }
  };

  return (
    <div className="modern-register-page">
      <div className="modern-register-container">
        <div className="modern-register-card">
          
          {/* Header */}
          <div className="modern-register-header">
            <div className="modern-logo">
              <LogoIcon />
            </div>
            <h1 className="modern-register-title">Create an account</h1>
            <p className="modern-register-subtitle">
              Already have an account? <Link to="/login" className="modern-login-link">Sign in</Link>
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="modern-error-message">
              {error}
            </div>
          )}

          {/* Registration Form */}
          <form onSubmit={handleSubmit} className="modern-register-form">
            
            {/* Name Field */}
            <div className="modern-form-group">
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Enter your full name"
                className="modern-form-input"
                required
              />
            </div>

            {/* Email Field */}
            <div className="modern-form-group">
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="Enter your email"
                className="modern-form-input"
                required
              />
            </div>

            {/* Phone Field */}
            <div className="modern-form-group">
              <div className="modern-phone-group">
                <select
                  name="country_code"
                  value={formData.country_code}
                  onChange={handleChange}
                  className="modern-country-select"
                >
                  <option value="UG">🇺🇬 UG</option>
                  <option value="US">🇺🇸 US</option>
                  <option value="UK">🇬🇧 UK</option>
                </select>
                <input
                  type="text"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleChange}
                  placeholder="700 000 000"
                  className="modern-phone-input"
                />
              </div>
            </div>

            {/* Password Fields */}
            <div className="modern-form-group">
              <div className="modern-password-group">
                <input
                  type={showPassword ? "text" : "password"}
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Create a password"
                  className="modern-form-input"
                  required
                />
                <button
                  type="button"
                  className="modern-password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  tabIndex="-1"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <div className="modern-form-group">
              <input
                type="password"
                name="confirm_password"
                value={formData.confirm_password}
                onChange={handleChange}
                placeholder="Confirm your password"
                className="modern-form-input"
                required
              />
            </div>

            {/* Terms Checkbox */}
            <div className="modern-terms-group">
              <label className="modern-checkbox-label">
                <input
                  type="checkbox"
                  name="termsAccepted"
                  checked={formData.termsAccepted}
                  onChange={handleChange}
                  className="modern-checkbox"
                />
                <span className="modern-checkbox-text">
                  I agree to <a href="/terms" className="modern-terms-link">Terms of Service</a> and <a href="/privacy" className="modern-terms-link">Privacy Policy</a>
                </span>
              </label>
            </div>

            {/* Submit Button */}
            <button type="submit" className="modern-submit-btn">
              Create Account
            </button>
          </form>

          {/* Divider */}
          <div className="modern-divider" style={{ marginTop: '20px' }}>
            <div className="modern-divider-line"></div>
            <span className="modern-divider-text">or sign up with</span>
            <div className="modern-divider-line"></div>
          </div>

          {/* Social Login */}
          <div className="modern-social-section" style={{ marginTop: '20px', marginBottom: '20px' }}>
            <div className="modern-social-buttons">
              <button type="button" className="modern-social-btn google-btn">
                <GoogleIcon />
                <span>Google</span>
              </button>
              <button type="button" className="modern-social-btn apple-btn">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                  <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
                </svg>
                <span>Apple</span>
              </button>
            </div>
          </div>

          {/* Footer */}
          <div className="modern-register-footer">
            <p className="modern-footer-text">
              Protected by reCAPTCHA and subject to Google <a href="/privacy" className="modern-terms-link">Privacy Policy</a> and <a href="/terms" className="modern-terms-link">Terms of Service</a>.
            </p>
          </div>

        </div>
      </div>

      {/* Success Modal */}
      {showSuccessModal && (
        <div className="success-modal-overlay">
          <div className="success-modal">
            <div className="success-icon">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="#10b981" strokeWidth="2"/>
                <path d="M8 12l2 2 4-4" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h2 className="success-title">Registration Successful!</h2>
            <p className="success-message">
              Your account has been created successfully. You can now login with your credentials.
            </p>
            <button onClick={handleSuccessModalOk} className="success-ok-btn">
              OK
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Register;

