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
    property_type: searchParams.get('property_type') || ''
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
      if (isUniversity) {
        params.append('audience_type', 'university');
      } else {
        params.append('audience_type', 'public');
      }
      
      const res = await api.get(`/properties/search/?${params.toString()}`);
      setProperties(res.data.results || res.data);
    } catch (error) {
      console.error('Error searching properties:', error);
      
      // Fallback to mock data for demonstration
      setProperties([
        {
          id: 1,
          title: 'Modern Studio by Campus',
          price: '1200',
          bedrooms: 1,
          bathrooms: 1,
          property_type: 'Studio Room',
          image: 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80'
        },
        {
          id: 2,
          title: 'Single Room by Campus',
          price: '1200',
          bedrooms: 1,
          bathrooms: 1,
          property_type: 'Studio Room',
          image: 'https://images.unsplash.com/photo-1502672260266-1c1de2d93688?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80'
        },
        {
          id: 3,
          title: 'Double Room by Roena',
          price: '1200',
          bedrooms: 1,
          bathrooms: 1,
          property_type: 'Double Room',
          image: 'https://images.unsplash.com/photo-1513694203232-719a280e022f?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80'
        },
        {
          id: 4,
          title: 'Modern Title by Granps',
          price: '1200',
          bedrooms: 1,
          bathrooms: 1,
          property_type: 'Studio Room',
          image: 'https://images.unsplash.com/photo-1493809842364-78817add7ffb?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80'
        }
      ]);
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
            <div className="minimal-no-results">
              <p>No properties found matching your criteria.</p>
              <button className="minimal-clear-btn" onClick={() => {
                setFilters({ location: '', property_type: '' });
                setIsUniversity(false);
              }}>Clear Filters</button>
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
