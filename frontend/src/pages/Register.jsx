import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { Eye, EyeOff, Building2, AlertCircle, Mail, User, Phone, Lock, Key, ChevronDown, Check } from 'lucide-react';
import './Auth.css';

const GoogleIcon = () => (
  <svg viewBox="0 0 24 24" width="18" height="18" xmlns="http://www.w3.org/2000/svg">
    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
  </svg>
);

const UgandaFlag = () => (
  <svg viewBox="0 0 72 48" width="24" height="16" xmlns="http://www.w3.org/2000/svg">
    <rect width="72" height="48" fill="#ffffff"/>
    <g>
      <rect y="0" width="72" height="6.857" fill="#000000"/>
      <rect y="6.857" width="72" height="6.857" fill="#fcdc04"/>
      <rect y="13.714" width="72" height="6.857" fill="#d90000"/>
      <rect y="20.571" width="72" height="6.857" fill="#ffffff"/>
      <rect y="27.429" width="72" height="6.857" fill="#fcdc04"/>
      <rect y="34.286" width="72" height="6.857" fill="#d90000"/>
      <rect y="41.143" width="72" height="6.857" fill="#000000"/>
    </g>
    <circle cx="36" cy="24" r="10" fill="#ffffff" stroke="#000000" strokeWidth="0.5"/>
    <path d="M36 16 L37.5 22.5 L44 22.5 L38.75 26.5 L40.5 33 L36 29 L31.5 33 L33.25 26.5 L28 22.5 L34.5 22.5 Z" fill="#fcdc04"/>
  </svg>
);

const USFlag = () => (
  <svg viewBox="0 0 72 48" width="24" height="16" xmlns="http://www.w3.org/2000/svg">
    <rect width="72" height="48" fill="#ffffff"/>
    <g fill="#b22234">
      <rect y="0" width="72" height="3.692"/>
      <rect y="7.385" width="72" height="3.692"/>
      <rect y="14.769" width="72" height="3.692"/>
      <rect y="22.154" width="72" height="3.692"/>
      <rect y="29.538" width="72" height="3.692"/>
      <rect y="36.923" width="72" height="3.692"/>
      <rect y="44.308" width="72" height="3.692"/>
    </g>
    <rect width="28.8" height="25.846" fill="#3c3b6e"/>
    <g fill="#ffffff">
      {Array.from({ length: 50 }).map((_, i) => {
        const x = (i % 6) * 4.8 + 2.4;
        const y = Math.floor(i / 6) * 3.462 + 1.731;
        if (i >= 30 && (i % 6) >= 5) return null;
        return <circle key={i} cx={x} cy={y} r="0.8"/>;
      })}
    </g>
  </svg>
);

const UKFlag = () => (
  <svg viewBox="0 0 72 48" width="24" height="16" xmlns="http://www.w3.org/2000/svg">
    <rect width="72" height="48" fill="#012169"/>
    <path d="M0 0 L72 48 M72 0 L0 48" stroke="#ffffff" strokeWidth="4.8"/>
    <path d="M0 0 L72 48 M72 0 L0 48" stroke="#c8102e" strokeWidth="3.2"/>
    <path d="M36 0 V48 M0 24 H72" stroke="#ffffff" strokeWidth="8"/>
    <path d="M36 0 V48 M0 24 H72" stroke="#c8102e" strokeWidth="4.8"/>
  </svg>
);

const countries = [
  { code: 'UG', label: 'UG (+256)', flag: UgandaFlag },
  { code: 'US', label: 'US (+1)', flag: USFlag },
  { code: 'UK', label: 'UK (+44)', flag: UKFlag },
];

const Register = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    country_code: 'UG',
    phone_number: '',
    password: '',
    confirm_password: '',
    marital_status: 'single',
    secret_key: '',
    termsAccepted: false
  });

  const getPasswordStrength = (password) => {
    if (!password) return { score: 0, color: '#94a3b8', text: 'Enter a password' };
    
    let score = 0;
    if (password.length >= 6) score += 1;
    if (password.length >= 8) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[a-z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    
    let color = '#ef4444'; 
    let text = 'Weak password';
    
    if (score >= 4) {
      color = '#22c55e'; 
      text = 'Strong password';
    } else if (score >= 3) {
      color = '#f59e0b'; 
      text = 'Medium password';
    } else if (score >= 2) {
      color = '#eab308'; 
      text = 'Fair password';
    }
    
    return { score, color, text };
  };
  
  const [isAdmin, setIsAdmin] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showCountryDropdown, setShowCountryDropdown] = useState(false);
  const [error, setError] = useState(null);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [touched, setTouched] = useState({});
  const { register } = useContext(AuthContext);
  const navigate = useNavigate();

  const validators = {
    name: (v) => v.trim().length >= 2 && /^[a-zA-Z\s]+$/.test(v.trim()),
    email: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v),
    phone_number: (v) => v.trim().length >= 9 && /^[\d\s]+$/.test(v.trim()),
    password: (v) => getPasswordStrength(v).score >= 2,
    confirm_password: (v) => v === formData.password && v.length > 0,
    termsAccepted: (v) => v === true,
  };

  const isFieldValid = (name) => {
    if (!touched[name]) return null;
    const val = formData[name];
    const validator = validators[name];
    if (!validator) return null;
    return validator(val);
  };

  const getFieldClass = (name) => {
    const valid = isFieldValid(name);
    if (valid === null) return '';
    return valid ? ' valid' : ' invalid';
  };

  const showCheck = (name) => isFieldValid(name) === true;

  const handleChange = (e) => {
    const { name, type } = e.target;
    const value = type === 'checkbox' ? e.target.checked : e.target.value;
    setFormData({ ...formData, [name]: value });
    setTouched(prev => ({ ...prev, [name]: true }));
    
    if (name === 'isAdmin') {
      setFormData(prev => ({ ...prev, isAdmin: e.target.checked }));
    }
  };

  const handleSuccessModalOk = () => {
    setShowSuccessModal(false);
    navigate('/login');
  };

  const handleGoogleSignIn = () => {
    // Use the provided Google OAuth URL directly
    const googleOAuthUrl = 'https://accounts.google.com/v3/signin/accountchooser?access_type=offline&client_id=1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com&prompt=consent&redirect_uri=http%3A%2F%2Flocalhost%3A59619%2Foauth-callback&response_type=code&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcclog+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fexperimentsandconfigs&state=04b3195c-799b-4b55-8c73-c17540cdc30e&dsh=S-315381552%3A1778091977506284&o2v=2&service=lso&flowName=GeneralOAuthFlow&opparams=%253F&continue=https%3A%2F%2Faccounts.google.com%2Fsignin%2Foauth%2Fconsent%3Fauthuser%3Dunknown%26part%3DAJi8hANzXJekWcFY2lnZpLpVhx_wUqwIOrBWq_u2wFv29qhhj55azbdQYC0OHRlZS9HzpsLIHSkx9wSycYpCH_tvbWvv0gOrX_NLkRbSwbVEA6x6XH-d-RcdfTV0sj7TDvPJ7yUU0gvvPVBOYTILxa9qBLSwoCY3mAHAIn5IlI0JHJmiWLXgBd2GxTrff8ABtKIhVa0a4qZOXoseHOuKJraulMovMvHJCXDzxdfbL6U7od8whuWLxWd8zf0mTmIepKnloxuQdf9dQTrbGGkR7RvEx8JLr0uD25haPCX8vsnrhyhUseMytQqD1nQ7ownQNYiixZmtSVK-D7E6D7YxZqGnKDbh6x3TleAKd524Enc1mx3otL3iigT9rG9LiQuCUlCEleSnwzQvF9BhjPHWwsOx7KYdVKYEOJU3ebWclI7Vk9WKTT0vXI6ydpfe1tceZ8cAC-XxgdsXj6sEKd7_jdIH8ylF7_cnC6r5-EG2NFd6siVRWlvAbhFfIIWhl86DZ3usYDQPZzI3%26flowName%3DGeneralOAuthFlow%26as%3DS-315381552%253A1778091977506284%26client_id%3D1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com%26requestPath%3D%252Fsignin%252Foauth%252Fconsent%23&app_domain=http%3A%2F%2Flocalhost%3A59619';
    
    // Open Google OAuth in new window
    window.open(googleOAuthUrl, '_blank', 'width=500,height=600');
  };

  const handleAppleSignIn = () => {
    // Apple Sign In URL (using Apple's OAuth flow)
    const appleOAuthUrl = 'https://appleid.apple.com/auth/authorize?client_id=com.nestoria.app&redirect_uri=http%3A%2F%2Flocalhost%3A59619%2Foauth-callback&response_type=code&scope=name%20email&response_mode=form_post';
    
    // Open Apple OAuth in new window
    window.open(appleOAuthUrl, '_blank', 'width=500,height=600');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!formData.name.trim() || !formData.email.trim() || !formData.password.trim()) {
      setError('Please fill in all required fields.');
      return;
    }

    if (!formData.termsAccepted) {
      setError('You must accept terms & conditions to register.');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('Please enter a valid email address.');
      return;
    }

    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match. Please check and try again.');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long.');
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
      
      if (isAdmin) {
        submitData.append('role', 'admin');
        if (formData.secret_key) {
          submitData.append('secret_key', formData.secret_key);
        }
      } else {
        submitData.append('role', 'tenant');
      }
      
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
          setError(errorData.detail || errorData.error || 'Registration failed. Please try again.');
        }
      } else {
        setError('Unable to connect to server. Please check your internet connection and try again.');
      }
    }
  };

  return (
    <div className="premium-auth-container">
      <div className="premium-auth-card premium-register-card animate-fade-in">
        
        <div className="premium-auth-header">
          <div className="premium-logo">
            <Building2 size={28} color="#ffffff" strokeWidth={2.5} />
          </div>
          <h2>Create an account</h2>
          <p>Join Nestoria today and unlock premium features</p>
        </div>

        {error && (
          <div className="premium-error-message">
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="premium-auth-form">
          
          <div className="premium-input-group">
            <label>Full Name</label>
            <div className={`premium-input-wrapper${getFieldClass('name')}`}>
              <User className="premium-input-icon" size={20} />
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="John Doe"
                required
              />
              {showCheck('name') && (
                <Check className="premium-check-icon" size={20} />
              )}
            </div>
          </div>

          <div className="premium-input-group">
            <label>Email Address</label>
            <div className={`premium-input-wrapper${getFieldClass('email')}`}>
              <Mail className="premium-input-icon" size={20} />
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="name@example.com"
                required
              />
              {showCheck('email') && (
                <Check className="premium-check-icon" size={20} />
              )}
            </div>
          </div>

          <div className="premium-input-group">
            <label>Phone Number</label>
            <div className="premium-phone-group">
              <div className="premium-country-dropdown">
                <button
                  type="button"
                  className="premium-country-trigger"
                  onClick={() => setShowCountryDropdown(!showCountryDropdown)}
                >
                  {(() => {
                    const selected = countries.find(c => c.code === formData.country_code);
                    const Flag = selected ? selected.flag : UgandaFlag;
                    return <Flag />;
                  })()}
                  <span>{formData.country_code}</span>
                  <ChevronDown size={16} className={showCountryDropdown ? 'rotate' : ''} />
                </button>
                {showCountryDropdown && (
                  <div className="premium-country-options">
                    {countries.map((country) => {
                      const Flag = country.flag;
                      return (
                        <button
                          key={country.code}
                          type="button"
                          className={`premium-country-option ${formData.country_code === country.code ? 'active' : ''}`}
                          onClick={() => {
                            setFormData({ ...formData, country_code: country.code });
                            setShowCountryDropdown(false);
                          }}
                        >
                          <Flag />
                          <span>{country.label}</span>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
              <div className={`premium-input-wrapper${getFieldClass('phone_number')}`} style={{flex: 1}}>
                <Phone className="premium-input-icon" size={20} />
                <input
                  type="text"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleChange}
                  placeholder="700 000 000"
                />
                {showCheck('phone_number') && (
                  <Check className="premium-check-icon" size={20} />
                )}
              </div>
            </div>
          </div>

          <div className="premium-input-group">
            <label>Marital Status</label>
            <div className="premium-radio-group">
              <label className="premium-radio-label">
                <input
                  type="radio"
                  name="marital_status"
                  value="single"
                  checked={formData.marital_status === 'single'}
                  onChange={handleChange}
                />
                <span>Single</span>
              </label>
              <label className="premium-radio-label">
                <input
                  type="radio"
                  name="marital_status"
                  value="married"
                  checked={formData.marital_status === 'married'}
                  onChange={handleChange}
                />
                <span>Married</span>
              </label>
            </div>
          </div>

          <div className="premium-input-group">
            <label>Password</label>
            <div className={`premium-input-wrapper${getFieldClass('password')}`}>
              <Lock className="premium-input-icon" size={20} />
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                required
                style={{ paddingRight: showCheck('password') ? '72px' : '44px' }}
              />
              {showCheck('password') && (
                <Check className="premium-check-icon" size={20} />
              )}
              <button
                type="button"
                className="premium-password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex="-1"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            <span className="premium-password-strength" style={{ color: getPasswordStrength(formData.password).color }}>
              {getPasswordStrength(formData.password).text}
            </span>
          </div>

          <div className="premium-input-group">
            <label>Confirm Password</label>
            <div className={`premium-input-wrapper${getFieldClass('confirm_password')}`}>
              <Lock className="premium-input-icon" size={20} />
              <input
                type="password"
                name="confirm_password"
                value={formData.confirm_password}
                onChange={handleChange}
                placeholder="••••••••"
                required
              />
              {showCheck('confirm_password') && (
                <Check className="premium-check-icon" size={20} />
              )}
            </div>
          </div>

          {/* Admin Section (Placed before terms) */}
          <div className="premium-input-group" style={{ marginTop: '8px' }}>
            <label className="premium-checkbox-label">
              <input
                type="checkbox"
                name="isAdmin"
                checked={isAdmin}
                onChange={handleChange}
              />
              <span>I am registering as an administrator (requires secret key)</span>
            </label>
          </div>

          {isAdmin && (
            <div className="premium-input-group">
              <label>Admin Secret Key</label>
              <div className="premium-input-wrapper">
                <Key className="premium-input-icon" size={20} />
                <input
                  type="text"
                  name="secret_key"
                  value={formData.secret_key || ''}
                  onChange={handleChange}
                  placeholder="Enter your administrator secret key"
                />
              </div>
            </div>
          )}

          {/* Terms Section (Placed after admin/secret key) */}
          <div className="premium-input-group" style={{ marginTop: '8px' }}>
            <label className={`premium-checkbox-label${getFieldClass('termsAccepted')}`}>
              <input
                type="checkbox"
                name="termsAccepted"
                checked={formData.termsAccepted}
                onChange={handleChange}
              />
              <span>I agree to the <Link to="/terms">Terms of Service</Link> and <Link to="/privacy">Privacy Policy</Link></span>
              {showCheck('termsAccepted') && (
                <Check className="premium-check-inline" size={16} />
              )}
            </label>
          </div>

          <button type="submit" className="premium-submit-btn">
            Create Account
          </button>
        </form>

        <div className="premium-divider">
          <span>or continue with</span>
        </div>

        <div className="premium-social-group">
          <button type="button" className="premium-social-btn" onClick={handleGoogleSignIn}>
            <GoogleIcon />
            <span>Google</span>
          </button>
          <button type="button" className="premium-social-btn" onClick={handleAppleSignIn}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
              <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
            </svg>
            <span>Apple</span>
          </button>
        </div>

        <div className="premium-auth-footer">
          <p>Already have an account? <Link to="/login">Sign in here</Link></p>
        </div>

      </div>

      {showSuccessModal && (
        <div className="success-modal-overlay" style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(15, 23, 42, 0.6)', backdropFilter: 'blur(4px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50
        }}>
          <div className="success-modal" style={{
            background: 'white', padding: '40px', borderRadius: '16px',
            textAlign: 'center', maxWidth: '400px', width: '90%',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
          }}>
            <div className="success-icon" style={{
              width: '64px', height: '64px', background: '#dcfce7',
              borderRadius: '50%', display: 'flex', alignItems: 'center',
              justifyContent: 'center', margin: '0 auto 24px'
            }}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 6L9 17l-5-5" stroke="#16a34a" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h2 style={{fontSize: '1.5rem', fontWeight: '700', color: '#0f172a', marginBottom: '12px'}}>Registration Successful!</h2>
            <p style={{color: '#64748b', marginBottom: '32px', lineHeight: '1.5'}}>
              Your account has been created successfully. You can now login with your credentials.
            </p>
            <button onClick={handleSuccessModalOk} className="premium-submit-btn">
              Continue to Login
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Register;
