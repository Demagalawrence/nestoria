import React, { useState, useEffect } from 'react';
import PropertyCard from './PropertyCard';
import api from '../api/axios';
import './MostViewed.css';

const MostViewed = () => {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);

  // Mock data matching the design image in case API is unavailable or empty
  const defaultProperties = [
    {
      id: 1,
      title: 'Ocean Breeze Villa',
      location: '123 Kololo Hill, Kampala',
      price: 'UGX 910,000',
      bedrooms: 4,
      bathrooms: 2,
      image: 'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 2,
      title: 'Jakson House',
      location: '4550 Nakasero Road, Kampala',
      price: 'UGX 750,000',
      bedrooms: 3,
      bathrooms: 2,
      image: 'https://images.unsplash.com/photo-1613490908571-9ce224924a1e?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 3,
      title: 'Lakeside Cottage',
      location: '7500 Lake Drive, Jinja',
      price: 'UGX 540,000',
      bedrooms: 3,
      bathrooms: 1,
      image: 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80'
    }
  ];

  useEffect(() => {
    const fetchProperties = async () => {
      try {
        const response = await api.get('/properties/');
        // Assuming Django REST Framework pagination or array
        const items = response.data.results || response.data; 
        if (items && items.length > 0) {
          setProperties(items.slice(0, 3)); // Get top 3
          setLoading(false);
          return;
        }
      } catch (error) {
        console.error("Failed to fetch properties, using fallback data", error);
      }
      
      // Fallback
      setProperties(defaultProperties);
      setLoading(false);
    };

    fetchProperties();
  }, []);

  return (
    <section className="most-viewed container">
      <div className="section-header text-center">
        <h2 className="section-title">Most Viewed</h2>
        <p className="section-subtitle">
          Discover a range of vacation homes worldwide. Reserve securely and get<br/>
          expert customer support for a stress-free stay.
        </p>
      </div>
      
      <div className="properties-grid">
        {loading ? (
          <div className="loader">Loading properties...</div>
        ) : (
          properties.map((prop, idx) => (
            <div key={prop.id || idx} className={`animate-fade-in delay-${(idx + 1) * 100}`}>
              <PropertyCard property={prop} />
            </div>
          ))
        )}
      </div>
      
      <div className="pagination-dots">
        <span className="dot active"></span>
        <span className="dot"></span>
        <span className="dot"></span>
      </div>
    </section>
  );
};

export default MostViewed;
