import React from 'react';
import { useLocation } from 'react-router-dom';
import './Footer.css';

const Footer = () => {
  const location = useLocation();
  
  if (location.pathname === '/admin') {
    return null;
  }

  return (
    <footer className="global-unified-footer">
      <div className="footer-content-container">
        <div className="f-logo-section">
          <div className="f-brand">
            <span className="f-icon"></span>
            <h2>NESTORIA</h2>
          </div>
          <p className="f-tagline">Your premier destination for property e-commerce.</p>
        </div>
        
        <div className="f-links-section">
          <div className="f-column">
            <h3>Company</h3>
            <a href="/about">About Us</a>
            <a href="/location">Locations</a>
          </div>
          <div className="f-column">
            <h3>Support</h3>
            <a href="/support">Help Center</a>
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
          </div>
        </div>
        
              </div>
      <div className="f-bottom-bar">
        <p>&copy; 2026 Nestoria Home E-Commerce. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;
