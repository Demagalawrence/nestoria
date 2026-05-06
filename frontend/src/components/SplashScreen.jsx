import React, { useState, useEffect } from 'react';
import { Home } from 'lucide-react';
import './SplashScreen.css';

const SplashScreen = ({ finishLoading }) => {
  const [isFadingOut, setIsFadingOut] = useState(false);

  useEffect(() => {
    // Start fading out after 2.5 seconds
    const fadeOutTimer = setTimeout(() => {
      setIsFadingOut(true);
    }, 2500);

    // Completely remove from DOM after 3 seconds (2.5 + 0.5s fade out)
    const removeTimer = setTimeout(() => {
      finishLoading();
    }, 3000);

    return () => {
      clearTimeout(fadeOutTimer);
      clearTimeout(removeTimer);
    };
  }, [finishLoading]);

  return (
    <div className={`splash-screen-container ${isFadingOut ? 'fade-out' : ''}`}>
      <div className="splash-content">
        <div className="splash-logo-wrapper">
          <Home className="splash-logo-icon" size={64} />
        </div>
        <h1 className="splash-title">Nestoria</h1>
        <p className="splash-subtitle">Find Your Perfect Home</p>
        
        <div className="splash-loader">
          <div className="splash-loader-bar"></div>
        </div>
      </div>
    </div>
  );
};

export default SplashScreen;
