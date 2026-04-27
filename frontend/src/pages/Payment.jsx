import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { CreditCard, Shield, ArrowLeft, CheckCircle, AlertCircle } from 'lucide-react';
import api from '../api/axios';
import BookingProgress from '../components/BookingProgress';
import './Payment.css';

const Payment = () => {
  const { bookingId } = useParams();
  const navigate = useNavigate();
  const [booking, setBooking] = useState(null);
  const [property, setProperty] = useState(null);
  const [paymentData, setPaymentData] = useState({
    card_number: '',
    expiry_date: '',
    cvv: '',
    cardholder_name: '',
    billing_address: ''
  });
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [receipt, setReceipt] = useState(null);
  const [showNotification, setShowNotification] = useState(false);

  useEffect(() => {
    fetchBookingDetails();
  }, [bookingId]);

  const fetchBookingDetails = async () => {
    try {
      console.log('Fetching booking details for booking ID:', bookingId);
      
      // Fetch booking details
      const bookingRes = await api.get(`/bookings/${bookingId}/`);
      console.log('Booking data received:', bookingRes.data);
      setBooking(bookingRes.data);

      // Fetch property details with better error handling
      const propertyId = bookingRes.data.rental_property || bookingRes.data.property;
      const propertyName = bookingRes.data.property_name;
      console.log('Property ID from booking:', propertyId);
      console.log('Property name from booking:', propertyName);
      
      if (propertyId) {
        // Use property ID if available
        const propertyRes = await api.get(`/properties/${propertyId}/`);
        console.log('Property data received:', propertyRes.data);
        setProperty(propertyRes.data);
      } else if (propertyName) {
        // Fallback: search property by name if ID is missing
        console.log('Searching for property by name:', propertyName);
        try {
          const searchRes = await api.get(`/properties/?search=${encodeURIComponent(propertyName)}`);
          const properties = searchRes.data?.results || searchRes.data || [];
          const foundProperty = properties.find(p => p.title === propertyName || p.name === propertyName);
          
          if (foundProperty) {
            console.log('Property found by name:', foundProperty);
            setProperty(foundProperty);
          } else {
            console.log('Property not found by name, using basic info from booking');
            // Create a minimal property object from booking data
            setProperty({
              title: propertyName,
              name: propertyName,
              id: 'unknown'
            });
          }
        } catch (searchError) {
          console.error('Error searching property by name:', searchError);
          // Create a minimal property object from booking data
          setProperty({
            title: propertyName,
            name: propertyName,
            id: 'unknown'
          });
        }
      } else {
        console.error('No property information found in booking data');
        setError('Booking is missing property information');
        return;
      }
    } catch (error) {
      console.error('Error fetching booking details:', error);
      if (error.response?.status === 404) {
        setError('Booking not found or property information is missing');
      } else {
        setError('Could not load booking information');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setPaymentData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const formatCardNumber = (value) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    const matches = v.match(/\d{4,16}/g);
    const match = matches && matches[0] || '';
    const parts = [];
    for (let i = 0, len = match.length; i < len; i += 4) {
      parts.push(match.substring(i, i + 4));
    }
    if (parts.length) {
      return parts.join(' ');
    } else {
      return v;
    }
  };

  const handleCardNumberChange = (e) => {
    const formatted = formatCardNumber(e.target.value);
    setPaymentData(prev => ({
      ...prev,
      card_number: formatted
    }));
  };

  const formatExpiryDate = (value) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    if (v.length >= 2) {
      return v.substring(0, 2) + '/' + v.substring(2, 4);
    }
    return v;
  };

  const handleExpiryDateChange = (e) => {
    const formatted = formatExpiryDate(e.target.value);
    setPaymentData(prev => ({
      ...prev,
      expiry_date: formatted
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setProcessing(true);
    setError(null);

    try {
      // Refresh booking data to get current status
      const freshBookingRes = await api.get(`/bookings/${bookingId}/`);
      const freshBooking = freshBookingRes.data;
      
      // First, confirm the booking if it's pending
      if (freshBooking.status === 'pending') {
        await api.post(`/bookings/${bookingId}/confirm/`);
      }

      // Create payment
      const paymentPayload = {
        booking: parseInt(bookingId),
        payment_method: 'credit_card'
      };

      const paymentRes = await api.post('/payments/create/', paymentPayload);
      
      if (paymentRes.data.id) {
        // Process payment (in real app, this would integrate with Stripe)
        const processRes = await api.post('/payments/process/', {
          payment_id: paymentRes.data.id
        });

        if (processRes.data.success) {
          // Show success notification
          setShowNotification(true);
          
          // Fetch receipt details
          try {
            const receiptRes = await api.get(`/payments/receipt/${paymentRes.data.id}/`);
            setReceipt(receiptRes.data);
          } catch (receiptError) {
            console.error('Error fetching receipt:', receiptError);
            // Use process response data as fallback
            setReceipt({
              receipt_number: processRes.data.receipt_number,
              payment_id: processRes.data.payment_id,
              amount: booking.final_amount || booking.total_amount,
              payment_method: 'credit_card',
              payment_date: new Date().toISOString()
            });
          }
          setSuccess(true);
          
          // Hide notification after 5 seconds and redirect
          setTimeout(() => {
            setShowNotification(false);
            navigate('/dashboard');
          }, 5000);
        }
      }
    } catch (error) {
      console.error('Error processing payment:', error);
      setError(error.response?.data?.detail || error.response?.data?.message || error.response?.data?.error || error.message || 'Payment failed. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="payment-container">
        <div className="loader">Loading payment information...</div>
      </div>
    );
  }

  if (error && !booking) {
    return (
      <div className="payment-container">
        <div className="error-message">{error}</div>
        <button onClick={() => navigate('/dashboard')} className="btn-secondary">
          Back to Dashboard
        </button>
      </div>
    );
  }

  if (success) {
    return (
      <div className="payment-container">
        <div className="success-message">
          <CheckCircle />
          <h2>Payment Successful!</h2>
          <p>Your booking has been confirmed and payment processed.</p>
          
          {receipt && (
            <div className="receipt-details">
              <h3>Payment Receipt</h3>
              <div className="receipt-item">
                <span>Receipt Number:</span>
                <span>{receipt.receipt_number}</span>
              </div>
              <div className="receipt-item">
                <span>Payment ID:</span>
                <span>{receipt.payment_id}</span>
              </div>
              <div className="receipt-item">
                <span>Amount Paid:</span>
                <span>${receipt.amount}</span>
              </div>
              <div className="receipt-item">
                <span>Payment Method:</span>
                <span>{receipt.payment_method}</span>
              </div>
              <div className="receipt-item">
                <span>Payment Date:</span>
                <span>{new Date(receipt.payment_date).toLocaleString()}</span>
              </div>
              <div className="receipt-item">
                <span>Booking Status:</span>
                <span className="status-confirmed">Confirmed</span>
              </div>
            </div>
          )}
          
          <p>Redirecting to dashboard in 5 seconds...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="payment-container">
      {/* Success Notification */}
      {showNotification && (
        <div className="payment-success-notification">
          <div className="notification-content">
            <div className="notification-icon">✅</div>
            <div className="notification-text">
              <h3>Payment Successful!</h3>
              <p>Your payment has been processed successfully. Booking confirmed!</p>
              <p>Receipt: {receipt?.receipt_number || 'Generating...'}</p>
            </div>
            <button 
              className="notification-close"
              onClick={() => setShowNotification(false)}
            >
              ×
            </button>
          </div>
        </div>
      )}
      
      <div className="payment-header">
        <button onClick={() => navigate(`/booking/${bookingId}`)} className="back-btn">
          <ArrowLeft /> Back to Booking
        </button>
        <h1>Complete Payment</h1>
      </div>

      <BookingProgress currentStep={3} />

      <div className="payment-content">
        <div className="payment-form-section">
          <div className="booking-summary">
            <h3>Booking Summary</h3>
            <div className="summary-item">
              <span>Property:</span>
              <span>{property?.name || property?.title || booking?.property_name || 'Property'}</span>
            </div>
            <div className="summary-item">
              <span>Check-in:</span>
              <span>{booking?.start_date || 'Not set'}</span>
            </div>
            <div className="summary-item">
              <span>Check-out:</span>
              <span>{booking?.end_date || 'Not set'}</span>
            </div>
            <div className="summary-item">
              <span>Guests:</span>
              <span>{booking?.number_of_occupants || booking?.number_of_guests || 1}</span>
            </div>
            <div className="summary-item total">
              <span>Total Amount:</span>
              <span>UGX {booking?.final_amount || booking?.total_amount || 0}</span>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="payment-form">
            <h3>Payment Information</h3>
            
            <div className="form-group">
              <label>
                <CreditCard /> Card Number
              </label>
              <input
                type="text"
                name="card_number"
                value={paymentData.card_number}
                onChange={handleCardNumberChange}
                placeholder="1234 5678 9012 3456"
                maxLength="19"
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Expiry Date</label>
                <input
                  type="text"
                  name="expiry_date"
                  value={paymentData.expiry_date}
                  onChange={handleExpiryDateChange}
                  placeholder="MM/YY"
                  maxLength="5"
                  required
                />
              </div>
              <div className="form-group">
                <label>CVV</label>
                <input
                  type="text"
                  name="cvv"
                  value={paymentData.cvv}
                  onChange={handleInputChange}
                  placeholder="123"
                  maxLength="4"
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label>Cardholder Name</label>
              <input
                type="text"
                name="cardholder_name"
                value={paymentData.cardholder_name}
                onChange={handleInputChange}
                placeholder="John Doe"
                required
              />
            </div>

            <div className="form-group">
              <label>Billing Address</label>
              <textarea
                name="billing_address"
                value={paymentData.billing_address}
                onChange={handleInputChange}
                placeholder="123 Main Street, City, State, ZIP"
                rows={3}
                required
              />
            </div>

            {error && (
              <div className="error-message">
                <AlertCircle />
                {error}
              </div>
            )}

            <button 
              type="submit" 
              className="btn-primary payment-submit"
              disabled={processing}
            >
              {processing ? (
                <>
                  <div className="spinner"></div>
                  Processing Payment...
                </>
              ) : (
                <>
                  <Shield /> Pay UGX {booking?.final_amount || booking?.total_amount || 0}
                </>
              )}
            </button>
          </form>
        </div>

        <div className="payment-security">
          <h3>Security & Trust</h3>
          <div className="security-features">
            <div className="security-item">
              <Shield />
              <div>
                <h4>Secure Payment</h4>
                <p>Your payment information is encrypted and secure</p>
              </div>
            </div>
            <div className="security-item">
              <CheckCircle />
              <div>
                <h4>SSL Protected</h4>
                <p>All transactions are protected by SSL encryption</p>
              </div>
            </div>
            <div className="security-item">
              <CreditCard />
              <div>
                <h4>Multiple Payment Methods</h4>
                <p>We accept all major credit and debit cards</p>
              </div>
            </div>
          </div>

          <div className="payment-info">
            <h4>Payment Information</h4>
            <ul>
              <li>Your card will be charged immediately</li>
              <li>You'll receive a confirmation email</li>
              <li>Free cancellation up to 24 hours before check-in</li>
              <li>Refund processed according to cancellation policy</li>
            </ul>
          </div>

          <div className="accepted-cards">
            <h4>We Accept</h4>
            <div className="card-logos">
              <div className="card-logo visa">VISA</div>
              <div className="card-logo mastercard">Mastercard</div>
              <div className="card-logo amex">AMEX</div>
              <div className="card-logo discover">Discover</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Payment;
