import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Hero.css';

const Hero = () => {
  const navigate = useNavigate();

  return (
    <section className="hero-section">
      <div className="hero-overlay"></div>
      <div className="container hero-content">
        <h1 className="hero-title animate-fade-in">Finding Your New<br/>Home Is Simple</h1>
        <p className="hero-subtitle animate-fade-in delay-100">
          RentHomes.com is your go-to destination for finding the<br/>
          perfect rental home to suit your needs.<br/>
          With thousands of property listings across Uganda<br/>
          and East Africa.
        </p>
        
        <div className="hero-search-wrapper animate-fade-in delay-200">
          <button className="hero-search-btn" onClick={() => navigate('/search')}>
            <span>Search</span>
            <div className="arrow-line">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>
            </div>
          </button>
        </div>
      </div>
    </section>
  );
};

export default Hero;
