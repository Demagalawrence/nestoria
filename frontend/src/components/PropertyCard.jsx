import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { MapPin, Star } from 'lucide-react';
import { AuthContext } from '../context/AuthContext';
import './PropertyCard.css';

const PropertyCard = ({ property }) => {
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);
  
  // Use property data or fallback to mock data
  const title = property.name || property.title || 'Modern Title by Granps';
  
  // Room availability details
  const type = property.property_type || 'Studio Room';
  const totalRooms = property.total_rooms || 10;
  const availableRooms = property.available_rooms !== undefined ? property.available_rooms : totalRooms;
  
  // Image handling
  const fallbackImages = [
    'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1502672260266-1c1de2d93688?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1513694203232-719a280e022f?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1493809842364-78817add7ffb?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1484154218962-a197022b5858?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1501183638710-841dd1904471?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80'
  ];
  const imageIndex = property.id ? property.id % fallbackImages.length : 0;
  
  // Use primary_image.image if it exists and is not a default/blank value, else fallback
  const imageUrl = property.primary_image?.image || property.image || property.image_url || fallbackImages[imageIndex];

  // Price formatting
  const priceValue = property.rent_per_month || property.price || '1,200';
  const formattedPrice = typeof priceValue === 'number' 
    ? Number(priceValue).toLocaleString('en-US') 
    : priceValue;
  const priceDisplay = `UGX ${formattedPrice}/mo`;

  const handleMapClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    // In a real app, this would open a map modal or redirect to a map view
    alert(`Showing map for ${title}`);
  };

  const handleReserveClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!user) {
      // User is not logged in, show login prompt
      alert('Please login to reserve this room. You will be redirected to the login page.');
      navigate('/login');
      return;
    }
    
    // User is logged in, proceed to reservation
    navigate(`/booking/${property.id}`);
  };

  const handleRatingClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    navigate(`/reviews/${property.id}`);
  };

  // Rating display logic
  const averageRating = property.average_rating || 0;
  const totalReviews = property.total_reviews || 0;
  
  const renderStars = (rating) => {
    return (
      <div className="rating-stars">
        {[1, 2, 3, 4, 5].map(star => (
          <Star
            key={star}
            size={14}
            className={star <= rating ? 'star-filled' : 'star-empty'}
            fill={star <= rating ? '#fbbf24' : 'none'}
            color={star <= rating ? '#fbbf24' : '#e2e8f0'}
          />
        ))}
      </div>
    );
  };

  return (
    <Link to={`/property/${property.id}`} className="minimal-property-card">
      <div className="minimal-card-image-wrapper">
        <img src={imageUrl} alt={title} className="minimal-card-image" />
      </div>
      
      <div className="minimal-card-content">
        <h3 className="minimal-card-title">{title}</h3>
        
        <p className="minimal-card-details">
          Type: {type} | Available: {availableRooms} out of {totalRooms} rooms empty
        </p>
        
        <p className="minimal-card-price">
          Price: <strong>{priceDisplay}</strong>
        </p>
        
        {/* Rating Display */}
        <div className="minimal-card-rating" onClick={handleRatingClick}>
          {renderStars(averageRating)}
          <span className="rating-text">
            {averageRating > 0 ? `${averageRating.toFixed(1)} (${totalReviews} reviews)` : 'No reviews yet'}
          </span>
        </div>
        
        <div className="minimal-card-actions">
          <button className="minimal-btn map-btn" onClick={handleMapClick}>
            <MapPin size={14} className="map-icon" /> map
          </button>
          
          <button className="minimal-btn reserve-btn" onClick={handleReserveClick}>
            Reserve this Room
          </button>
        </div>
      </div>
    </Link>
  );
};

export default PropertyCard;
