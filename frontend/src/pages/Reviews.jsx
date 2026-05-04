import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Star, MapPin, Bed, Bath, User, Calendar, ThumbsUp, MessageSquare, Filter } from 'lucide-react';
import api from '../api/axios';
import './Reviews.css';

const Reviews = () => {
  const { propertyId } = useParams();
  const [property, setProperty] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('recent');
  const [reviewForm, setReviewForm] = useState({
    rating: 5,
    title: '',
    content: ''
  });

  useEffect(() => {
    if (propertyId) {
      fetchPropertyReviews();
    } else {
      fetchUserReviews();
    }
  }, [propertyId]);

  const fetchPropertyReviews = async () => {
    try {
      // Fetch property details
      const propertyRes = await api.get(`/properties/${propertyId}/`);
      setProperty(propertyRes.data);

      // Fetch property reviews
      const reviewsRes = await api.get(`/properties/${propertyId}/reviews/`);
      setReviews(reviewsRes.data.results || reviewsRes.data);
    } catch (error) {
      console.error('Error fetching reviews:', error);
      // Mock data for demonstration
      setProperty({
        id: propertyId,
        title: 'Ocean Breeze Villa',
        location: '123 Main Street, Anytown'
      });
      setReviews([
        {
          id: 1,
          user: 'John Doe',
          rating: 5,
          title: 'Amazing Property!',
          content: 'Absolutely loved our stay here. The property was clean, well-maintained, and exactly as described. Would definitely reserve again!',
          cleanliness: 5,
          communication: 5,
          check_in: 5,
          location: 5,
          value: 5,
          created_at: '2 weeks ago',
          helpful_count: 12,
          user_avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-4.0.3&auto=format&fit=crop&w=100&q=80'
        },
        {
          id: 2,
          user: 'Jane Smith',
          rating: 4,
          title: 'Great Experience',
          content: 'Very nice property with good amenities. Location was convenient and the host was responsive. Minor issues with WiFi but overall great stay.',
          cleanliness: 4,
          communication: 5,
          check_in: 5,
          location: 4,
          value: 4,
          created_at: '1 month ago',
          helpful_count: 8,
          user_avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?ixlib=rb-4.0.3&auto=format&fit=crop&w=100&q=80'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserReviews = async () => {
    try {
      const res = await api.get('/reviews/user/');
      setReviews(res.data.results || res.data);
    } catch (error) {
      console.error('Error fetching user reviews:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    try {
      const reviewData = {
        rating: reviewForm.rating,
        title: reviewForm.title,
        review: reviewForm.content,
        rental_property: parseInt(propertyId)
      };
      
      const res = await api.post(`/properties/${propertyId}/add-review/`, reviewData);
      if (res.data.id) {
        setReviews(prev => [res.data, ...prev]);
        setShowReviewForm(false);
        setReviewForm({
          rating: 5,
          title: '',
          content: ''
        });
      }
    } catch (error) {
      console.error('Error submitting review:', error);
    }
  };

  const renderStars = (rating, interactive = false, onChange) => {
    return (
      <div className="stars">
        {[1, 2, 3, 4, 5].map(star => (
          <Star
            key={star}
            size={interactive ? 20 : 16}
            className={star <= rating ? 'filled' : 'empty'}
            onClick={() => interactive && onChange(star)}
            style={interactive ? { cursor: 'pointer' } : {}}
          />
        ))}
      </div>
    );
  };

  const filteredAndSortedReviews = reviews
    .filter(review => {
      if (filter === 'all') return true;
      if (filter === '5') return review.rating === 5;
      if (filter === '4') return review.rating === 4;
      if (filter === '3') return review.rating <= 3;
      return true;
    })
    .sort((a, b) => {
      if (sortBy === 'recent') return new Date(b.created_at) - new Date(a.created_at);
      if (sortBy === 'rating_high') return b.rating - a.rating;
      if (sortBy === 'rating_low') return a.rating - b.rating;
      return 0;
    });

  const averageRating = reviews.length > 0
    ? (reviews.reduce((sum, review) => sum + review.rating, 0) / reviews.length).toFixed(1)
    : 0;

  const ratingDistribution = [5, 4, 3, 2, 1].map(rating => ({
    rating,
    count: reviews.filter(r => r.rating === rating).length,
    percentage: reviews.length > 0 ? (reviews.filter(r => r.rating === rating).length / reviews.length) * 100 : 0
  }));

  if (loading) {
    return (
      <div className="reviews-container">
        <div className="loader">Loading reviews...</div>
      </div>
    );
  }

  return (
    <div className="reviews-container">
      {propertyId && property && (
        <div className="reviews-header">
          <div className="property-info">
            <Link to={`/property/${propertyId}`} className="property-link">
              ← Back to Property
            </Link>
            <h1>{property.title}</h1>
            <p><MapPin size={16} /> {property.location}</p>
          </div>
        </div>
      )}

      <div className="reviews-overview">
        <div className="rating-summary">
          <div className="average-rating">
            <div className="rating-number">{averageRating}</div>
            {renderStars(Math.round(averageRating))}
            <div className="rating-text">{reviews.length} review{reviews.length !== 1 ? 's' : ''}</div>
          </div>
          
          <div className="rating-bars">
            {ratingDistribution.map(({ rating, count, percentage }) => (
              <div key={rating} className="rating-bar">
                <div className="rating-label">
                  {renderStars(rating)}
                  <span>{rating}</span>
                </div>
                <div className="bar-container">
                  <div className="bar-fill" style={{ width: `${percentage}%` }}></div>
                </div>
                <span className="count">{count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="review-actions">
          <button className="btn-primary" onClick={() => setShowReviewForm(true)}>
            <Star /> Write a Review
          </button>
        </div>
      </div>

      <div className="reviews-controls">
        <div className="filter-controls">
          <div className="filter-group">
            <Filter size={16} />
            <select value={filter} onChange={(e) => setFilter(e.target.value)}>
              <option value="all">All Ratings</option>
              <option value="5">5 Stars</option>
              <option value="4">4 Stars</option>
              <option value="3">3 Stars & Below</option>
            </select>
          </div>
          
          <div className="sort-group">
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="recent">Most Recent</option>
              <option value="rating_high">Highest Rating</option>
              <option value="rating_low">Lowest Rating</option>
            </select>
          </div>
        </div>
      </div>

      <div className="reviews-list">
        {filteredAndSortedReviews.length === 0 ? (
          <div className="no-reviews">
            <MessageSquare size={48} />
            <h3>No reviews yet</h3>
            <p>Be the first to share your experience!</p>
          </div>
        ) : (
          filteredAndSortedReviews.map(review => (
            <div key={review.id} className="review-card">
              <div className="review-header">
                <div className="reviewer-info">
                  <img
                    src={review.user_avatar || `https://ui-avatars.com/api/?name=${review.user_name || review.user}&background=1D4ED8&color=fff`}
                    alt={review.user_name || review.user}
                    className="reviewer-avatar"
                  />
                  <div className="reviewer-details">
                    <h4>{review.user_name || review.user}</h4>
                    <div className="review-date">{new Date(review.created_at).toLocaleDateString()}</div>
                  </div>
                </div>
                <div className="review-rating">
                  {renderStars(review.rating)}
                </div>
              </div>

              <div className="review-content">
                <h5>{review.title}</h5>
                <p>{review.review || review.content}</p>
              </div>


            </div>
          ))
        )}
      </div>

      {showReviewForm && (
        <div className="review-modal-overlay">
          <div className="review-modal">
            <div className="modal-header">
              <h2>Write a Review</h2>
              <button className="close-btn" onClick={() => setShowReviewForm(false)}>
                ×
              </button>
            </div>

            <form onSubmit={handleReviewSubmit} className="review-form">
              <div className="form-group">
                <label>Overall Rating</label>
                {renderStars(reviewForm.rating, true, (rating) =>
                  setReviewForm(prev => ({ ...prev, rating }))
                )}
              </div>

              <div className="form-group">
                <label>Review Title</label>
                <input
                  type="text"
                  value={reviewForm.title}
                  onChange={(e) => setReviewForm(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="Summarize your experience"
                  required
                />
              </div>

              <div className="form-group">
                <label>Your Review</label>
                <textarea
                  value={reviewForm.content}
                  onChange={(e) => setReviewForm(prev => ({ ...prev, content: e.target.value }))}
                  placeholder="Tell us about your experience"
                  rows={5}
                  required
                />
              </div>



              <div className="form-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowReviewForm(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Submit Review
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Reviews;
