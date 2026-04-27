import React from 'react';
import { MapPin, Phone, Mail, Clock } from 'lucide-react';
import './Location.css';

const Location = () => {
  return (
    <div className="location-page">
      <div className="container">
        <div className="location-header">
          <h1>Our Locations</h1>
          <p>Find us in cities across the United States and Europe</p>
        </div>
        
        <div className="location-content">
          <div className="location-map">
            <div className="map-placeholder">
              <MapPin size={48} />
              <h3>Interactive Map</h3>
              <p>Explore our properties across different cities</p>
            </div>
          </div>
          
          <div className="location-list">
            <div className="location-section">
              <h2>United States</h2>
              <div className="cities-grid">
                <div className="city-item">
                  <h3>New York</h3>
                  <div className="city-info">
                    <div className="info-item">
                      <MapPin size={16} />
                      <span>Manhattan, Brooklyn, Queens</span>
                    </div>
                    <div className="info-item">
                      <Phone size={16} />
                      <span>+1 (555) 123-4567</span>
                    </div>
                    <div className="info-item">
                      <Mail size={16} />
                      <span>ny@renthu.com</span>
                    </div>
                  </div>
                  <div className="city-stats">
                    <span className="stat">2,500+ Properties</span>
                    <span className="stat">15,000+ Tenants</span>
                  </div>
                </div>
                
                <div className="city-item">
                  <h3>Los Angeles</h3>
                  <div className="city-info">
                    <div className="info-item">
                      <MapPin size={16} />
                      <span>Hollywood, Santa Monica, Beverly Hills</span>
                    </div>
                    <div className="info-item">
                      <Phone size={16} />
                      <span>+1 (555) 987-6543</span>
                    </div>
                    <div className="info-item">
                      <Mail size={16} />
                      <span>la@renthu.com</span>
                    </div>
                  </div>
                  <div className="city-stats">
                    <span className="stat">1,800+ Properties</span>
                    <span className="stat">12,000+ Tenants</span>
                  </div>
                </div>
                
                <div className="city-item">
                  <h3>Chicago</h3>
                  <div className="city-info">
                    <div className="info-item">
                      <MapPin size={16} />
                      <span>Loop, Lincoln Park, Lakeview</span>
                    </div>
                    <div className="info-item">
                      <Phone size={16} />
                      <span>+1 (555) 456-7890</span>
                    </div>
                    <div className="info-item">
                      <Mail size={16} />
                      <span>chicago@renthu.com</span>
                    </div>
                  </div>
                  <div className="city-stats">
                    <span className="stat">1,200+ Properties</span>
                    <span className="stat">8,000+ Tenants</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="location-section">
              <h2>Europe</h2>
              <div className="cities-grid">
                <div className="city-item">
                  <h3>London</h3>
                  <div className="city-info">
                    <div className="info-item">
                      <MapPin size={16} />
                      <span>Westminster, Camden, Shoreditch</span>
                    </div>
                    <div className="info-item">
                      <Phone size={16} />
                      <span>+44 20 7123 4567</span>
                    </div>
                    <div className="info-item">
                      <Mail size={16} />
                      <span>london@renthu.com</span>
                    </div>
                  </div>
                  <div className="city-stats">
                    <span className="stat">2,000+ Properties</span>
                    <span className="stat">10,000+ Tenants</span>
                  </div>
                </div>
                
                <div className="city-item">
                  <h3>Paris</h3>
                  <div className="city-info">
                    <div className="info-item">
                      <MapPin size={16} />
                      <span>Marais, Saint-Germain, Montmartre</span>
                    </div>
                    <div className="info-item">
                      <Phone size={16} />
                      <span>+33 1 42 68 53 42</span>
                    </div>
                    <div className="info-item">
                      <Mail size={16} />
                      <span>paris@renthu.com</span>
                    </div>
                  </div>
                  <div className="city-stats">
                    <span className="stat">1,500+ Properties</span>
                    <span className="stat">7,000+ Tenants</span>
                  </div>
                </div>
                
                <div className="city-item">
                  <h3>Berlin</h3>
                  <div className="city-info">
                    <div className="info-item">
                      <MapPin size={16} />
                      <span>Kreuzberg, Prenzlauer Berg, Mitte</span>
                    </div>
                    <div className="info-item">
                      <Phone size={16} />
                      <span>+49 30 1234567</span>
                    </div>
                    <div className="info-item">
                      <Mail size={16} />
                      <span>berlin@renthu.com</span>
                    </div>
                  </div>
                  <div className="city-stats">
                    <span className="stat">1,000+ Properties</span>
                    <span className="stat">5,000+ Tenants</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="location-cta">
          <div className="cta-content">
            <h2>Don't see your city?</h2>
            <p>We're constantly expanding to new locations. Let us know where you'd like us to be next!</p>
            <button className="btn-primary">Suggest a City</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Location;
