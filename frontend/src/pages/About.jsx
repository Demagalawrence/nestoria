import React, { useEffect } from 'react';
import './About.css';
import { Shield, Lightbulb, Users, Home, Search, Lock, Star, MessageSquare, BarChart } from 'lucide-react';

const About = () => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="about-page">
      {/* Premium Dark Gradient Header */}
      <div className="inner-page-hero">
        <div className="container hero-content-wrapper">
          <h1 className="inner-hero-title">About Nestoria</h1>
          <p className="inner-hero-subtitle">Your trusted partner in finding the perfect home, bringing clarity and confidence to the real estate market.</p>
        </div>
      </div>
      
      <div className="container about-main-container">
        <div className="about-content">
          
          <div className="about-section story-section">
            <div className="story-content">
              <h2>Our Story</h2>
              <p className="lead-text">
                Founded in 2024, Nestoria (formerly Rent H&U) was born from a simple idea: finding the perfect rental home should be easy, transparent, and stress-free.
              </p>
              <p>
                We started with just a handful of properties in Kampala and have grown to become a premium platform connecting thousands of tenants with their ideal homes across Uganda and East Africa. 
              </p>
              <p>
                Our mission is to revolutionize the rental experience by leveraging technology to create seamless connections between property owners and tenants, while ensuring safety, transparency, and unparalleled service for everyone involved.
              </p>
            </div>
            <div className="story-image-wrapper">
              <img src="https://images.unsplash.com/photo-1560518883-ce09059eeffa?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" alt="Modern Building" className="story-image" />
            </div>
          </div>
          
          <div className="about-section gray-bg-section">
            <h2>What We Do</h2>
            <div className="features-grid">
              <div className="feature-item">
                <div className="feature-icon"><Home size={28} /></div>
                <h3>Property Listings</h3>
                <p>Comprehensive property database with detailed information, high-quality photos, and virtual tours.</p>
              </div>
              <div className="feature-item">
                <div className="feature-icon"><Search size={28} /></div>
                <h3>Smart Search</h3>
                <p>Advanced filtering and search capabilities to find exactly what you're looking for with precision.</p>
              </div>
              <div className="feature-item">
                <div className="feature-icon"><Lock size={28} /></div>
                <h3>Secure Booking</h3>
                <p>Safe and secure booking process with verified landlords and robust payment protection.</p>
              </div>
              <div className="feature-item">
                <div className="feature-icon"><Star size={28} /></div>
                <h3>Reviews & Ratings</h3>
                <p>Transparent review system to help you make informed decisions based on real tenant experiences.</p>
              </div>
              <div className="feature-item">
                <div className="feature-icon"><MessageSquare size={28} /></div>
                <h3>24/7 Support</h3>
                <p>Round-the-clock customer support dedicated to assisting you with any questions or issues.</p>
              </div>
              <div className="feature-item">
                <div className="feature-icon"><BarChart size={28} /></div>
                <h3>Analytics</h3>
                <p>Detailed analytics and market insights for property owners to optimize their listings.</p>
              </div>
            </div>
          </div>
          
          <div className="about-section">
            <h2 className="text-center">Our Core Values</h2>
            <div className="values-grid">
              <div className="value-item">
                <div className="value-icon"><Shield size={36} /></div>
                <h3>Trust</h3>
                <p>We build trust through complete transparency, rigorous verification, and consistent, excellent service delivery.</p>
              </div>
              <div className="value-item">
                <div className="value-icon"><Lightbulb size={36} /></div>
                <h3>Innovation</h3>
                <p>We constantly push boundaries and innovate to improve the rental experience for everyone.</p>
              </div>
              <div className="value-item">
                <div className="value-icon"><Users size={36} /></div>
                <h3>Community</h3>
                <p>We foster a thriving community of happy tenants and successful, empowered property owners.</p>
              </div>
            </div>
          </div>
          
          <div className="about-section impact-section">
            <div className="impact-overlay"></div>
            <div className="impact-content">
              <h2>Our Impact in Numbers</h2>
              <div className="stats-grid">
                <div className="stat-item">
                  <div className="stat-number">10K+</div>
                  <div className="stat-label">Properties Listed</div>
                </div>
                <div className="stat-item">
                  <div className="stat-number">50K+</div>
                  <div className="stat-label">Happy Tenants</div>
                </div>
                <div className="stat-item">
                  <div className="stat-number">2K+</div>
                  <div className="stat-label">Property Owners</div>
                </div>
                <div className="stat-item">
                  <div className="stat-number">15+</div>
                  <div className="stat-label">Districts Covered</div>
                </div>
              </div>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  );
};

export default About;
