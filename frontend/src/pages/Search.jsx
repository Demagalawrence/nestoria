import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import PropertyCard from '../components/PropertyCard';
import api from '../api/axios';
import './Search.css';

const SearchResults = () => {
  const [searchParams] = useSearchParams();
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Custom states for the minimalist design
  const [isUniversity, setIsUniversity] = useState(false);
  const [filters, setFilters] = useState({
    location: searchParams.get('location') || '',
    property_type: searchParams.get('property_type') || '',
    max_price: searchParams.get('max_price') || ''
  });

  useEffect(() => {
    searchProperties();
    window.scrollTo(0, 0);
  }, [searchParams, isUniversity, filters]);

  const searchProperties = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      
      // Basic filtering for this minimalist layout
      if (filters.location) params.append('location', filters.location);
      if (filters.property_type) params.append('property_type', filters.property_type);
      if (filters.max_price) params.append('max_rent', filters.max_price);
      // Add audience filtering based on toggle
      params.append('audience_type', isUniversity ? 'university' : 'public');
      
      const res = await api.get(`/properties/search/?${params.toString()}`);
      setProperties(res.data.results || res.data);
    } catch (error) {
      console.error('Error searching properties:', error);
      
      // Remove mock data fallback
      setProperties([]);
      // Only set error if it's an actual error, not just an empty result
      if (error.response?.status !== 404) {
        setError('Failed to fetch properties from the server.');
      }
    } finally {
      setLoading(false);
    }
  };

  const toggleUniversity = () => {
    setIsUniversity(!isUniversity);
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="minimal-search-page">
      <div className="container">
        
        {/* Minimalist Inline Header */}
        <div className="minimal-search-header">
          <h1 className="minimal-page-title">All Properties</h1>
          
          <div className="minimal-filters-group">
            <span className="filter-label">Filter</span>
            
            <div className="minimal-select-wrapper">
              <select 
                name="location" 
                className="minimal-select" 
                value={filters.location}
                onChange={handleFilterChange}
              >
                <option value="">Location</option>
                <option value="Kampala">Kampala</option>
                <option value="Entebbe">Entebbe</option>
                <option value="Jinja">Jinja</option>
                <option value="Wakiso">Wakiso</option>
              </select>
            </div>
            
            <div className="minimal-select-wrapper">
              <select 
                name="property_type" 
                className="minimal-select" 
                value={filters.property_type}
                onChange={handleFilterChange}
              >
                <option value="">All Types</option>
                <option value="apartment">Apartment</option>
                <option value="house">Independent House</option>
                <option value="villa">Villa</option>
                <option value="hostel">Hostel</option>
                <option value="studio">Studio Apartment</option>
                <option value="single_room">Single Room</option>
                <option value="double_room">Double Room</option>
                <option value="self_contained">Self Contained</option>
              </select>
            </div>
            
            <div className="minimal-select-wrapper">
              <input 
                type="number"
                name="max_price" 
                className="minimal-input" 
                placeholder="Max Price (UGX)"
                value={filters.max_price}
                onChange={handleFilterChange}
              />
            </div>
          </div>
          
          <div className="minimal-toggle-group">
            <span className={`toggle-label ${isUniversity ? 'active' : ''}`}>UNIVERSITY</span>
            <div className={`minimal-toggle-switch ${isUniversity ? '' : 'public-active'}`} onClick={toggleUniversity}>
              <div className="toggle-slider"></div>
            </div>
            <span className={`toggle-label ${!isUniversity ? 'active' : ''}`}>PUBLIC</span>
          </div>
        </div>

        {/* Content Area */}
        <div className="minimal-search-content">
          {loading ? (
            <div className="minimal-loader">Loading properties...</div>
          ) : error ? (
            <div className="minimal-error">{error}</div>
          ) : properties.length === 0 ? (
            <div className="minimal-empty-state">
              <h3>No properties found</h3>
              <p>Try adjusting your filters or search criteria.</p>
            </div>
          ) : (
            <div className="minimal-properties-grid">
              {properties.map(property => (
                <PropertyCard key={property.id} property={property} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchResults;
