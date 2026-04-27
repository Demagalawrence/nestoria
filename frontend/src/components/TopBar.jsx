import React from 'react';
import { Clock, MapPin, Facebook, Instagram, Twitter, Youtube } from 'lucide-react';
import './TopBar.css';

const TopBar = () => {
  return (
    <div className="logisco-topbar">
      <div className="topbar-left">
        <div className="topbar-info-item">
          <Clock size={16} color="#ff7a00" />
          <span>Opening Hours: Mon-Fri 8am to 6pm - Closed on Weekends</span>
        </div>
        <div className="topbar-info-item loc-item">
          <MapPin size={16} color="#ff7a00" />
          <span>Location Near you: <strong>San Francisco &gt;</strong></span>
        </div>
      </div>
      
      <div className="topbar-right-bg"></div>
      <div className="topbar-right-content">
        <span className="reach-us">REACH US :</span>
        <div className="topbar-socials">
          <a href="#"><Facebook size={14} /></a>
          <a href="#"><Instagram size={14} /></a>
          <a href="#"><Twitter size={14} /></a>
          <a href="#"><Youtube size={14} /></a>
        </div>
      </div>
    </div>
  );
};

export default TopBar;
