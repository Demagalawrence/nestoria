import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
   Brain,
   Home as HomeIcon,
   Facebook,
   Instagram,
   Linkedin,
   Building2,
   Home,
   Palmtree,
   Tent
} from 'lucide-react';
import HeroNavbar from './HeroNavbar';
import personImage from '../assets/person.png';
import './HeroSection.css';

const HeroSection = () => {
   const navigate = useNavigate();

   const handleSearch = (e) => {
      e.preventDefault();
      const searchInput = e.target.querySelector('.search-input');
      if (searchInput && searchInput.value.trim()) {
         navigate(`/search?q=${encodeURIComponent(searchInput.value.trim())}`);
      }
   };
   return (
      <div className="nesttori-hero-section">
         {/* Background Image Overlay - dark green/black gradient on the left side */}
         <div className="nesttori-bg-overlay"></div>

         <div className="nesttori-content-wrapper">
            {/* Separated Navbar Component */}
            <HeroNavbar />

            {/* Hero Content */}
            <main className="nesttori-main-content">
               <div className="nesttori-hero-left">

                  <h1 className="nesttori-hero-title">
                     Find Your Perfect Stay,<br />
                     AnyWhere
                  </h1>

                  {/* Search Bar Section */}
                  <form className="search-bar-container" onSubmit={handleSearch}>
                     <input
                        type="text"
                        placeholder="Enter location, property type, or features (e.g., Downtown apartment, 3-bed family home with pool)"
                        className="search-input"
                     />
                     <button type="submit" className="search-btn">Search Now</button>
                  </form>

                  <p className="nesttori-explore-text">Explore thousands of listings by category. Verified Stays.</p>

                  {/* Categories Section */}
                  <div className="categories-row">
                     <div className="category-item brain-wrapper">
                        <div className="brain-container">
                           <Brain size={28} className="nesttori-brain-icon" strokeWidth={1.5} />
                           <HomeIcon size={10} className="brain-inner-home" strokeWidth={3} />
                        </div>
                     </div>

                     <div className="category-item">
                        <Building2 size={28} strokeWidth={1.5} className="cat-icon" />
                        <span>Apartments</span>
                     </div>

                     <div className="category-item">
                        <Home size={28} strokeWidth={1.5} className="cat-icon" />
                        <span>Family Homes</span>
                     </div>

                     <div className="category-item">
                        <Palmtree size={28} strokeWidth={1.5} className="cat-icon" />
                        <span>Villas</span>
                     </div>

                     <div className="category-item">
                        <Tent size={28} strokeWidth={1.5} className="cat-icon" />
                        <span>Unique Stays</span>
                     </div>
                  </div>
               </div>

               {/* Floating Property Cards placed at bottom center/right */}
               <div className="floating-properties-row">
                  {/* Bugema Self-Contained Rooms */}
                  <Link to="/property/bugema-self-contained" className="floating-card">
                     <img src="https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=400&q=80" alt="Bugema Self-Contained Rooms" className="prop-img" />
                     <div className="prop-details">
                        <div className="prop-header">
                           <span className="prop-price">ugx</span>
                           <span className="prop-badge">🏢</span>
                        </div>
                        <span className="prop-desc">Bugema Self-Contained Rooms, Private Bath, Kitchen Access</span>
                     </div>
                  </Link>

                  {/* Jinja Executive Hostels */}
                  <Link to="/property/jinja-executive-hostels" className="floating-card">
                     <img src="https://images.unsplash.com/photo-1566073791251-02c2a1b9a198?auto=format&fit=crop&w=400&q=80" alt="Jinja Executive Hostels" className="prop-img" />
                     <div className="prop-details">
                        <div className="prop-header">
                           <span className="prop-price">ugx</span>
                           <span className="prop-badge">🏠</span>
                        </div>
                        <span className="prop-desc">Jinja Executive Hostels, Modern Facilities, Study Areas</span>
                     </div>
                  </Link>

                  {/* Entebbe Airport Guest House */}
                  <Link to="/property/entebbe-airport-guest-house" className="floating-card">
                     <img src="https://images.unsplash.com/photo-1570124479644-e84f8208c7fa?auto=format&fit=crop&w=400&q=80" alt="Entebbe Airport Guest House" className="prop-img" />
                     <div className="prop-details">
                        <div className="prop-header">
                           <span className="prop-price">ugx</span>
                           <span className="prop-badge">�</span>
                        </div>
                        <span className="prop-desc">Entebbe Airport Guest House, 24/7 Shuttle, Airport Transfer</span>
                     </div>
                  </Link>

                  {/* Wakiso Student Hostels */}
                  <Link to="/property/wakiso-student-hostels" className="floating-card">
                     <img src="https://images.unsplash.com/photo-1551882547-3c0de63dc8ea?auto=format&fit=crop&w=400&q=80" alt="Wakiso Student Hostels" className="prop-img" />
                     <div className="prop-details">
                        <div className="prop-header">
                           <span className="prop-price">ugx</span>
                           <span className="prop-badge">🎓</span>
                        </div>
                        <span className="prop-desc">Wakiso Student Hostels, Budget Friendly, Near University</span>
                     </div>
                  </Link>
               </div>
            </main>

            {/* Person Image from Assets - Right Side */}
            <div className="right-side-person">
               <img
                  src={personImage}
                  alt="Person"
                  className="right-person-image"
               />
            </div>

            {/* Social Footer */}
            <footer className="nesttori-social-footer">
               <a href="https://facebook.com/NesttoriFB" target="_blank" rel="noopener noreferrer" className="social-item">
                  <div className="social-icon-circle">
                     <Facebook size={18} className="social-icon" strokeWidth={1.5} />
                  </div>
                  <span className="social-handle">@NesttoriFB</span>
               </a>
               <a href="https://instagram.com/NesttoriInsta" target="_blank" rel="noopener noreferrer" className="social-item">
                  <div className="social-icon-circle">
                     <Instagram size={18} className="social-icon" strokeWidth={1.5} />
                  </div>
                  <span className="social-handle">@NesttoriInsta</span>
               </a>
               <a href="https://linkedin.com/company/Nesttori_LI" target="_blank" rel="noopener noreferrer" className="social-item">
                  <div className="social-icon-circle">
                     <Linkedin size={18} className="social-icon" strokeWidth={1.5} />
                  </div>
                  <span className="social-handle">@Nesttori_LI</span>
               </a>
               <a href="https://twitter.com/NesttoriX" target="_blank" rel="noopener noreferrer" className="social-item">
                  <div className="social-icon-circle">
                     <span className="social-icon-x">𝕏</span>
                  </div>
                  <span className="social-handle">@NesttoriX</span>
               </a>
               <a href="https://tiktok.com/@NesttoriTikTok" target="_blank" rel="noopener noreferrer" className="social-item">
                  <div className="social-icon-circle">
                     <svg className="social-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M9 12a4 4 0 1 0 4 4V4a5 5 0 0 0 5 5"></path>
                     </svg>
                  </div>
                  <span className="social-handle">@NesttoriTikTok</span>
               </a>
            </footer>
         </div>
      </div>
   );
};

export default HeroSection;
