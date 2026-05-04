import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Calendar, Clock, Users, CreditCard, FileText, ArrowLeft } from 'lucide-react';
import api from '../api/axios';
import { AuthContext } from '../context/AuthContext';
import ReservationProgress from '../components/BookingProgress';
import './Booking.css';

const Booking = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, loading: authLoading } = useContext(AuthContext);
  const [property, setProperty] = useState(null);
  const [bookingData, setBookingData] = useState({
    start_date: '',
    end_date: '',
    number_of_occupants: 1,
    special_requests: '',
    rental_property: parseInt(id)
  });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [bookingId, setBookingId] = useState(null);
  const [redirectCountdown, setRedirectCountdown] = useState(2);
  const [availableRooms, setAvailableRooms] = useState([]);
  const [totalRooms, setTotalRooms] = useState(0);

  useEffect(() => {
    // Check if user is authenticated
    if (!authLoading && !user) {
      // Store the current booking URL to redirect back after login
      sessionStorage.setItem('redirectAfterLogin', `/booking/${id}`);
      navigate('/login', { 
        state: { 
          message: 'Please log in to book a property',
          from: `/booking/${id}`
        } 
      });
      return;
    }
    
    if (user) {
      fetchProperty();
    }
  }, [id, user, authLoading, navigate]);

  // Debug booking data changes
  useEffect(() => {
    console.log('Booking data updated:', bookingData);
  }, [bookingData]);


  const fetchProperty = async () => {
    try {
      const res = await api.get(`/properties/${id}/`);
      setProperty(res.data);
      
      // Skip rooms fetching since we're not using room selection
      console.log('Skipping rooms API call - using property-level booking');
    } catch (error) {
      console.error('Error fetching property:', error);
      setError('Could not load property information');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    console.log(`Form field changed: ${name} = ${value}`);
    setBookingData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const calculateTotalPrice = () => {
    if (!property || !bookingData.start_date || !bookingData.end_date) return 0;
    
    const checkIn = new Date(bookingData.start_date);
    const checkOut = new Date(bookingData.end_date);
    const nights = Math.ceil((checkOut - checkIn) / (1000 * 60 * 60 * 24));
    
    // Use property pricing directly - no room selection
    // Ensure we parse it safely, stripping commas if any
    const rawPrice = property.rent_per_month || property.price_per_night || property.price || 0;
    const priceStr = String(rawPrice).replace(/,/g, '');
    const pricePerMonth = parseFloat(priceStr) || 0;
    console.log(`Using property price: $${pricePerMonth}/month for ${nights} nights`);
    
    // Ensure price is reasonable and within database limits
    const safePrice = Math.min(pricePerMonth, 99999999); // Max 8 digits for UGX
    
    // Calculate total price based on property pricing
    let totalPrice;
    if (nights >= 30) {
      const months = Math.ceil(nights / 30);
      totalPrice = months * safePrice;
    } else {
      // Daily rate for short stays
      const dailyRate = safePrice / 30;
      totalPrice = nights * dailyRate;
    }
    
    // Ensure total price is within 10-digit limit
    const finalPrice = Math.min(Math.round(totalPrice), 999999999);
    console.log(`Final calculated price: $${finalPrice}`);
    return finalPrice;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const bookingPayload = {
        rental_property: parseInt(id),
        start_date: bookingData.start_date,
        end_date: bookingData.end_date,
        number_of_occupants: parseInt(bookingData.number_of_occupants),
        special_requests: bookingData.special_requests,
        base_rent: calculateTotalPrice(),
        monthly_rent: calculateTotalPrice(),
        booking_type: 'online'
      };

      // Room field removed - using property-level booking only
      console.log('Property-level booking - no room field needed');

      // Ensure rent values are properly formatted as decimals
      const totalPrice = calculateTotalPrice();
      console.log('Calculated total price:', totalPrice);
      
      // Ensure values are within 10-digit limit
      const baseRent = Math.min(parseFloat(totalPrice), 999999999);
      const monthlyRent = Math.min(parseFloat(totalPrice), 999999999);
      
      bookingPayload.base_rent = baseRent;
      bookingPayload.monthly_rent = monthlyRent;
      
      console.log('Base rent:', baseRent, 'length:', baseRent.toString().length);
      console.log('Monthly rent:', monthlyRent, 'length:', monthlyRent.toString().length);
      console.log('=== BOOKING SUBMISSION DEBUG ===');
      console.log('Booking payload:', bookingPayload);
      console.log('Dates being used:');
      console.log('  Start date:', bookingPayload.start_date);
      console.log('  End date:', bookingPayload.end_date);
      console.log('  Room ID:', bookingPayload.room);
      console.log('  Property ID:', bookingPayload.rental_property);
      console.log('  Number of occupants:', bookingPayload.number_of_occupants);
      console.log('  Base rent:', bookingPayload.base_rent);
      console.log('  Monthly rent:', bookingPayload.monthly_rent);
      console.log('Submitting booking request...');
      console.log('=== END BOOKING SUBMISSION DEBUG ===');
      
      const res = await api.post('/bookings/create/', bookingPayload);
      console.log('Booking response:', res.data);
      console.log('Booking response status:', res.status);
      
      if (res.data && res.data.id) {
        console.log('Booking successful! Full response:', res.data);
        console.log('Booking ID:', res.data.id);
        console.log('Rental property in response:', res.data.rental_property);
        
        // Show success message
        const bookingRef = res.data.booking_reference || `#${res.data.id}`;
        alert(`🎉 Room Reserved Successfully!\n\nBooking Reference: ${bookingRef}\nProperty: ${property?.name || property?.title || 'Property'}\n\nYou will be redirected to complete your payment.`);
        
        navigate(`/payment/${res.data.id}`);
      } else {
        console.log('Booking response missing ID:', res.data);
        setError('Booking created but missing booking ID. Please contact support.');
      }
    } catch (error) {
      console.error('=== BOOKING ERROR DEBUG ===');
      console.error('Error object:', error);
      console.error('Error message:', error.message);
      console.error('Error response:', error.response);
      console.error('Error response data:', error.response?.data);
      console.error('Error status:', error.response?.status);
      console.error('Error status text:', error.response?.statusText);
      console.error('Error headers:', error.response?.headers);
      console.error('Error config:', error.config);
      console.error('=== END ERROR DEBUG ===');
      
      // Show detailed error message
      const errorData = error.response?.data;
      console.log('Full error data:', JSON.stringify(errorData, null, 2));
      
      if (errorData) {
        if (typeof errorData === 'object') {
          const errorMessages = Object.entries(errorData)
            .map(([field, messages]) => {
              const friendlyField = field === 'non_field_errors' ? 'Booking' : field.charAt(0).toUpperCase() + field.slice(1);
              const messageText = Array.isArray(messages) ? messages.join(', ') : messages;
              console.log(`${field}: ${messageText}`);
              return `${friendlyField}: ${messageText}`;
            })
            .join('; ');
          setError(errorMessages);
        } else {
          setError(errorData.detail || errorData.error || 'Failed to create booking. Please try again.');
        }
      } else {
        setError(`Error: ${error.message || 'Failed to create booking. Please try again.'}`);
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (loading || authLoading) {
    return (
      <div className="modern-booking-page">
        <div className="modern-booking-container">
          <div className="loader">Loading...</div>
        </div>
      </div>
    );
  }

  if (error && !property) {
    return (
      <div className="modern-booking-page">
        <div className="modern-booking-container">
          <div className="modern-error-message">{error}</div>
          <button onClick={() => navigate(`/property/${id}`)} className="modern-back-btn">
            <ArrowLeft size={20} />
            <span>Back to Property</span>
          </button>
        </div>
      </div>
    );
  }

  // Remove this check for now to allow booking even if rooms API fails
  // if (property && availableRooms.length === 0) {
  //   return (
  //     <div className="modern-booking-page">
  //       <div className="modern-booking-container">
  //         <div className="modern-error-message">
  //           No rooms are currently available for this property. Please check back later or contact the property owner.
  //         </div>
  //         <button onClick={() => navigate(`/property/${id}`)} className="modern-back-btn">
  //           <ArrowLeft size={20} />
  //           <span>Back to Property</span>
  //         </button>
  //       </div>
  //     </div>
  //   );
  // }



  return (
    <div className="modern-booking-page">
      {/* Modern Header */}
      <div className="modern-booking-header">
        <div className="container">
          <button onClick={() => navigate(`/property/${id}`)} className="modern-back-btn">
            <ArrowLeft size={20} />
            <span>Back to Property</span>
          </button>
          
          <div className="modern-booking-title-section">
            <h1 className="modern-booking-title">Complete Your Reservation</h1>
            <p className="modern-booking-subtitle">Secure your stay at {property?.name || property?.title || 'Property'}</p>
          </div>
        </div>
      </div>

      <div className="container modern-booking-container">
        
        {/* Progress Bar */}
        <BookingProgress currentStep={2} />
        
        {/* Modern Content Layout */}
        <div className="modern-booking-layout">
          
          {/* Left Column - Booking Form */}
          <div className="modern-booking-form-section">
            
            {/* Property Card */}
            <div className="modern-property-card">
              <div className="property-image-container">
                <img 
                  src={property?.primary_image?.image || property?.image_url || 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80'} 
                  alt={property?.title || 'Property'} 
                  className="modern-property-image" 
                />
              </div>
              <div className="modern-property-info">
                <h3 className="modern-property-title">{property?.name || property?.title || 'Property'}</h3>
                <p className="modern-property-location">{property?.district || property?.location || 'Location'}</p>
                <p style={{ margin: '8px 0', fontSize: '14px', color: '#475569' }}>
                  Available: {property?.available_rooms !== undefined ? property.available_rooms : 10} out of {property?.total_rooms || 10} rooms empty | Occupied: {(property?.total_rooms || 10) - (property?.available_rooms !== undefined ? property.available_rooms : 10)}
                </p>
                <div className="modern-property-features">
                  <span className="modern-feature-badge">
                    <Users size={16} /> {property?.total_rooms || 1} Rooms
                  </span>
                  <span className="modern-feature-badge">
                    <Calendar size={16} /> {property?.property_type || 'Property'}
                  </span>
                </div>
              </div>
            </div>

            {/* Booking Form */}
            <form onSubmit={handleSubmit} className="modern-booking-form">
              <div className="modern-form-section">
                <h2 className="form-section-title">Booking Details</h2>
                
                <div className="modern-form-row">
                  <div className="modern-form-group">
                    <label className="modern-form-label">
                      <Calendar size={18} />
                      Check-in Date
                    </label>
                    <input
                      type="date"
                      name="start_date"
                      value={bookingData.start_date}
                      onChange={handleInputChange}
                      className="modern-form-input"
                      required
                      min={new Date().toISOString().split('T')[0]}
                    />
                  </div>
                  <div className="modern-form-group">
                    <label className="modern-form-label">
                      <Calendar size={18} />
                      Check-out Date
                    </label>
                    <input
                      type="date"
                      name="end_date"
                      value={bookingData.end_date}
                      onChange={handleInputChange}
                      className="modern-form-input"
                      required
                      min={bookingData.start_date || new Date().toISOString().split('T')[0]}
                    />
                  </div>
                </div>

                <div className="modern-form-row">
                  <div className="modern-form-group">
                    <label className="modern-form-label">
                      <Users size={18} />
                      Number of Guests
                    </label>
                    <select
                      name="number_of_occupants"
                      value={bookingData.number_of_occupants}
                      onChange={handleInputChange}
                      className="modern-form-select"
                      required
                    >
                      <option value={1}>1 Guest</option>
                      <option value={2}>2 Guests</option>
                      <option value={3}>3 Guests</option>
                      <option value={4}>4 Guests</option>
                      <option value={5}>5+ Guests</option>
                    </select>
                  </div>
                </div>

                <div className="modern-form-group full-width">
                  <label className="modern-form-label">
                    <FileText size={18} />
                    Special Requests (Optional)
                  </label>
                  <textarea
                    name="special_requests"
                    value={bookingData.special_requests}
                    onChange={handleInputChange}
                    className="modern-form-textarea"
                    placeholder="Any special requirements or requests..."
                    rows={4}
                  />
                </div>
              </div>

              {error && (
                <div className="modern-error-message">{error}</div>
              )}

              <button 
                type="submit" 
                className="modern-submit-btn"
                disabled={submitting || (availableRooms.length === 0 && (!property?.available_rooms || property?.available_rooms === 0))}
                style={(availableRooms.length === 0 && (!property?.available_rooms || property?.available_rooms === 0)) ? {backgroundColor: '#ccc', cursor: 'not-allowed'} : {}}
              >
                {submitting ? (
                  <>
                    <Clock className="modern-spinner" /> 
                    Creating Booking...
                  </>
                ) : (
                  <>
                    <CreditCard size={20} /> 
                    Continue to Payment
                  </>
                )}
              </button>
            </form>
          </div>
          
          {/* Right Column - Summary */}
          <div className="modern-booking-summary">
            <div className="modern-summary-card">
              <h3 className="summary-title">Booking Summary</h3>
              
              <div className="summary-section">
                <h4 className="summary-section-title">Property Details</h4>
                <div className="summary-item">
                  <span className="summary-label">Property:</span>
                  <span className="summary-value">{property?.name || property?.title || 'Property'}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Location:</span>
                  <span className="summary-value">{property?.district || property?.location || 'Location'}</span>
                </div>
              </div>
              
              <div className="summary-section">
                <h4 className="summary-section-title">Booking Dates</h4>
                <div className="summary-item">
                  <span className="summary-label">Check-in:</span>
                  <span className="summary-value">{bookingData.start_date || 'Not selected'}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Check-out:</span>
                  <span className="summary-value">{bookingData.end_date || 'Not selected'}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Guests:</span>
                  <span className="summary-value">{bookingData.number_of_occupants}</span>
                </div>
                              </div>
              
              <div className="summary-section price-section">
                <h4 className="summary-section-title">Price Breakdown</h4>
                <div className="price-item">
                  <span className="price-label">Price per night:</span>
                  <span className="price-value">${property?.price_per_night || property?.price || 100}</span>
                </div>
                {bookingData.start_date && bookingData.end_date && (
                  <div className="price-item">
                    <span className="price-label">Number of nights:</span>
                    <span className="price-value">
                      {Math.ceil((new Date(bookingData.end_date) - new Date(bookingData.start_date)) / (1000 * 60 * 60 * 24))}
                    </span>
                  </div>
                )}
                <div className="price-item total-price">
                  <span className="price-label total-label">Total Amount:</span>
                  <span className="price-value total-value">${calculateTotalPrice()}</span>
                </div>
              </div>

              <div className="booking-policies">
                <h4 className="policies-title">Booking Policies</h4>
                <ul className="policies-list">
                  <li>Free cancellation up to 24 hours before check-in</li>
                  <li>Payment required to confirm booking</li>
                  <li>Confirmation will be sent to your email</li>
                  <li>Property owner will be notified of your booking</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Booking;
