import React, { useState, useEffect, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Calendar, MapPin, CreditCard, ChevronRight, AlertCircle, CheckCircle2, Clock, XCircle, Star } from 'lucide-react';
import api from '../api/axios';
import { AuthContext } from '../context/AuthContext';
import './Reservations.css';

const Reservations = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cancellingId, setCancellingId] = useState(null);
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    // Redirect if not logged in
    if (!user) {
      navigate('/login', { state: { from: '/reservations' } });
      return;
    }
    
    fetchBookings();
  }, [user, navigate]);

  const fetchBookings = async () => {
    try {
      setLoading(true);
      const res = await api.get('/bookings/');
      
      // Handle both paginated and direct array responses
      const bookingsData = res.data?.results ? res.data.results : (Array.isArray(res.data) ? res.data : []);
      
      // Sort by creation date (newest first) if not already sorted
      const sortedBookings = bookingsData.sort((a, b) => {
        return new Date(b.created_at || b.booking_date) - new Date(a.created_at || a.booking_date);
      });
      
      // Filter out cancelled bookings so they disappear from the view
      const activeBookings = sortedBookings.filter(booking => booking.status?.toLowerCase() !== 'cancelled');
      
      setBookings(activeBookings);
    } catch (err) {
      console.error('Error fetching reservations:', err);
      setError('Could not load your reservations. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch(status?.toLowerCase()) {
      case 'confirmed': return <CheckCircle2 size={18} className="status-icon confirmed" />;
      case 'pending': return <Clock size={18} className="status-icon pending" />;
      case 'cancelled': return <XCircle size={18} className="status-icon cancelled" />;
      case 'completed': return <CheckCircle2 size={18} className="status-icon completed" />;
      default: return <AlertCircle size={18} className="status-icon default" />;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const handleCancelBooking = async (bookingId, bookingReference) => {
    // Show confirmation dialog
    const isConfirmed = window.confirm(
      `Are you sure you want to cancel booking ${bookingReference || '#' + bookingId}?\n\nThis action cannot be undone.`
    );
    
    if (!isConfirmed) return;
    
    try {
      setCancellingId(bookingId);
      console.log(`Attempting to cancel booking ${bookingId}...`);
      
      // Call API to cancel booking
      const response = await api.post(`/bookings/${bookingId}/cancel/`, {
        cancellation_reason: 'User requested cancellation'
      });
      
      console.log('Cancel booking response:', response);
      
      // Remove the cancelled booking from the list immediately
      console.log('Removing booking from local state:', bookingId);
      setBookings(prevBookings => {
        const updatedBookings = prevBookings.filter(booking => booking.id !== bookingId);
        console.log('Bookings after removal:', updatedBookings);
        return updatedBookings;
      });
      
      // Show success message regardless of API response format
      alert(`Booking ${bookingReference || '#' + bookingId} has been cancelled successfully and removed from your reservations.`);
      
      // If response doesn't have expected format, still consider it successful
      if (!response.data || !response.data.message) {
        console.warn('API response format unexpected, but proceeding with local update');
      }
    } catch (error) {
      console.error('=== CANCEL BOOKING ERROR DEBUG ===');
      console.error('Error object:', error);
      console.error('Error response:', error.response);
      console.error('Error status:', error.response?.status);
      console.error('Error data:', error.response?.data);
      console.error('Error message:', error.message);
      
      let errorMessage = 'Failed to cancel booking. Please try again or contact support.';
      let shouldRemoveCard = false;
      
      if (error.response?.status === 401) {
        errorMessage = 'Authentication error. Please log in again.';
      } else if (error.response?.status === 403) {
        errorMessage = 'Permission denied. You cannot cancel this booking.';
      } else if (error.response?.status === 404) {
        errorMessage = 'Booking not found - removing from your list.';
        shouldRemoveCard = true; // Remove card if booking doesn't exist
      } else if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      }
      
      // If booking doesn't exist on server, remove it from local list
      if (shouldRemoveCard) {
        console.log('Removing card due to 404 error - booking not found on server');
        setBookings(prevBookings => 
          prevBookings.filter(booking => booking.id !== bookingId)
        );
      }
      
      alert(errorMessage);
    } finally {
      setCancellingId(null);
    }
  };

  if (loading) {
    return (
      <div className="reservations-page">
        <div className="reservations-header-section">
          <div className="reservations-container">
            <h1 className="page-title">My Reservations</h1>
            <p className="page-subtitle">Manage your current and past bookings</p>
          </div>
        </div>
        <div className="reservations-container">
          <div className="reservations-loader">
            <div className="loader-spinner"></div>
            <p>Loading your reservations...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="reservations-page">
      <div className="reservations-header-section">
        <div className="reservations-container">
          <h1 className="page-title">My Reservations</h1>
          <p className="page-subtitle">Manage your current and past bookings</p>
        </div>
      </div>

      <div className="reservations-container">
        {error && (
          <div className="error-message">
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        {!error && bookings.length === 0 ? (
          <div className="empty-reservations">
            <div className="empty-state-icon">
              <Calendar size={48} />
            </div>
            <h2>No Reservations Found</h2>
            <p>Looks like you haven't booked any properties yet. Start exploring our premium properties today!</p>
            <button className="browse-btn" onClick={() => navigate('/search')}>
              Browse Properties
            </button>
          </div>
        ) : (
          <div className="reservations-grid">
            {bookings.map((booking) => (
              <div key={booking.id} className="reservation-card">
                <div className="reservation-header">
                  <div className="reservation-id">
                    <span className="label">Booking Ref:</span>
                    <span className="value">{booking.booking_reference || `#${booking.id}`}</span>
                  </div>
                  <div className={`reservation-status ${booking.status?.toLowerCase()}`}>
                    {getStatusIcon(booking.status)}
                    <span>{booking.status || 'Unknown'}</span>
                  </div>
                </div>

                <div className="reservation-body">
                  <h3 className="property-name">{booking.property_name || `Property #${booking.rental_property}`}</h3>
                  
                  {booking.room_number && (
                    <div className="room-info">
                      <span className="room-badge">Room {booking.room_number}</span>
                    </div>
                  )}

                  <div className="reservation-details">
                    <div className="detail-row">
                      <div className="detail-icon"><Calendar size={16} /></div>
                      <div className="detail-text">
                        <span className="detail-label">Check In:</span>
                        <span className="detail-value">{formatDate(booking.start_date || booking.check_in_date)}</span>
                      </div>
                    </div>
                    
                    <div className="detail-row">
                      <div className="detail-icon"><Calendar size={16} /></div>
                      <div className="detail-text">
                        <span className="detail-label">Check Out:</span>
                        <span className="detail-value">{formatDate(booking.end_date || booking.check_out_date)}</span>
                      </div>
                    </div>

                    <div className="detail-row">
                      <div className="detail-icon"><CreditCard size={16} /></div>
                      <div className="detail-text">
                        <span className="detail-label">Total Amount:</span>
                        <span className="detail-value price">${booking.final_amount || booking.total_amount || booking.base_rent || '0'}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="reservation-footer">
                  <div className="payment-status">
                    <span className="label">Payment:</span>
                    <span className={`status-badge ${booking.payment_status?.toLowerCase() || 'pending'}`}>
                      {booking.payment_status || 'Pending'}
                    </span>
                  </div>
                  <div className="reservation-actions">
                    {booking.status?.toLowerCase() !== 'cancelled' && booking.status?.toLowerCase() !== 'completed' ? (
                      <button 
                        className="cancel-booking-btn"
                        onClick={() => handleCancelBooking(booking.id, booking.booking_reference)}
                        disabled={cancellingId === booking.id}
                      >
                        {cancellingId === booking.id ? (
                          <>
                            <div className="spinner-small"></div>
                            Cancelling...
                          </>
                        ) : (
                          <>
                            <XCircle size={16} />
                            Cancel Booking
                          </>
                        )}
                      </button>
                    ) : null}
                    
                    {booking.status?.toLowerCase() === 'completed' && (
                      <button 
                        className="view-details-btn rate-property-btn"
                        onClick={() => navigate(`/reviews/${booking.rental_property || booking.property}`)}
                        style={{ backgroundColor: '#ff9800', marginRight: '10px', color: 'white', border: 'none' }}
                      >
                        <Star size={16} style={{ marginRight: '5px' }} /> Rate
                      </button>
                    )}
                    
                    <button 
                      className="view-details-btn"
                      onClick={() => navigate(`/payment/${booking.id}`)}
                    >
                      View Details <ChevronRight size={16} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Reservations;
