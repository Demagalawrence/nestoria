import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, X } from 'lucide-react';
import './FloatingSearch.css';
import './FloatingSearchInputs.css';

const FloatingSearch = () => {
  const [searchData, setSearchData] = useState({
    location: '',
    property_type: '',
    min_price: '',
    max_price: '',
    bedrooms: '',
    bathrooms: '',
    amenities: '',
    city: '',
    country: ''
  });
  const [showAdvanced, setShowAdvanced] = useState(false);
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSearchData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSearch = () => {
    const params = new URLSearchParams();
    
    // Add all search parameters
    Object.keys(searchData).forEach(key => {
      if (searchData[key]) {
        params.append(key, searchData[key]);
      }
    });
    
    // Navigate to search results with parameters
    navigate(`/search?${params.toString()}`);
  };

  const handleClear = () => {
    setSearchData({
      location: '',
      property_type: '',
      min_price: '',
      max_price: '',
      bedrooms: '',
      bathrooms: '',
      amenities: '',
      city: '',
      country: ''
    });
  };

  const hasActiveFilters = Object.values(searchData).some(value => value !== '');

  return (
    <div className="search-wrapper container">
      <div className="search-container glass-panel animate-fade-in delay-300">
        <div className="search-main">
          <div className="search-field">
            <label>Location <span className="chevron">▼</span></label>
            <input 
              type="text" 
              placeholder="City, address, or neighborhood" 
              name="location"
              value={searchData.location}
              onChange={handleInputChange}
              className="search-input blank-input" 
            />
          </div>
          
          <div className="search-divider"></div>
          
          <div className="search-field">
            <label>Property Type <span className="chevron">▼</span></label>
            <select 
              name="property_type"
              value={searchData.property_type} 
              onChange={handleInputChange} 
              className="search-input blank-select"
            >
              <option value="">Any type</option>
              <option value="apartment">Apartment</option>
              <option value="house">House</option>
              <option value="villa">Villa</option>
              <option value="studio">Studio</option>
              <option value="hostel">Hostel</option>
              <option value="hotel">Hotel</option>
            </select>
          </div>
          
          <div className="search-divider"></div>
          
          <div className="search-field price-range">
            <label>Price Range <span className="chevron">▼</span></label>
            <div className="price-inputs">
              <input 
                type="number" 
                placeholder="Min" 
                name="min_price"
                value={searchData.min_price}
                onChange={handleInputChange}
                className="search-input blank-input price-input" 
              />
              <span className="price-separator">-</span>
              <input 
                type="number" 
                placeholder="Max" 
                name="max_price"
                value={searchData.max_price}
                onChange={handleInputChange}
                className="search-input blank-input price-input" 
              />
            </div>
          </div>
          
          <button onClick={handleSearch} className="search-submit-btn">
            <Search size={20} />
            Search
          </button>
        </div>

        <div className="search-advanced-toggle">
          <button 
            type="button" 
            className="advanced-toggle-btn"
            onClick={() => setShowAdvanced(!showAdvanced)}
          >
            <Filter size={16} />
            {showAdvanced ? 'Hide' : 'Show'} Advanced Filters
          </button>
          {hasActiveFilters && (
            <button type="button" className="clear-filters-btn" onClick={handleClear}>
              <X size={16} />
              Clear All
            </button>
          )}
        </div>

        {showAdvanced && (
          <div className="search-advanced animate-fade-in">
            <div className="advanced-grid">
              <div className="search-field">
                <label>Bedrooms</label>
                <select 
                  name="bedrooms"
                  value={searchData.bedrooms} 
                  onChange={handleInputChange} 
                  className="search-input blank-select"
                >
                  <option value="">Any</option>
                  <option value="1">1+</option>
                  <option value="2">2+</option>
                  <option value="3">3+</option>
                  <option value="4">4+</option>
                  <option value="5">5+</option>
                </select>
              </div>
              
              <div className="search-field">
                <label>Bathrooms</label>
                <select 
                  name="bathrooms"
                  value={searchData.bathrooms} 
                  onChange={handleInputChange} 
                  className="search-input blank-select"
                >
                  <option value="">Any</option>
                  <option value="1">1+</option>
                  <option value="2">2+</option>
                  <option value="3">3+</option>
                  <option value="4">4+</option>
                </select>
              </div>
              
              <div className="search-field">
                <label>City</label>
                <input 
                  type="text" 
                  placeholder="e.g. Kampala" 
                  name="city"
                  value={searchData.city}
                  onChange={handleInputChange}
                  className="search-input blank-input" 
                />
              </div>
              
              <div className="search-field">
                <label>Country</label>
                <input 
                  type="text" 
                  placeholder="e.g. Uganda" 
                  name="country"
                  value={searchData.country}
                  onChange={handleInputChange}
                  className="search-input blank-input" 
                />
              </div>
              
              <div className="search-field full-width">
                <label>Amenities</label>
                <input 
                  type="text" 
                  placeholder="WiFi, Parking, Pool, Gym, etc." 
                  name="amenities"
                  value={searchData.amenities}
                  onChange={handleInputChange}
                  className="search-input blank-input" 
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FloatingSearch;
