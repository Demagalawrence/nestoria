import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { CreditCard, Shield, ArrowLeft, CheckCircle, AlertCircle } from 'lucide-react';
import api from '../api/axios';
import ReservationProgress from '../components/BookingProgress';
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
  const [selectedMethod, setSelectedMethod] = useState('1');
  const [paymentStep, setPaymentStep] = useState(1);
  const [mobileMoneyNumber, setMobileMoneyNumber] = useState('');
  const [timeLeft, setTimeLeft] = useState(600); // 10 minutes
  const [isExpired, setIsExpired] = useState(false);

  const mockSavedMethods = [
    { id: '1', type: 'visa', logo: 'VISA', number: 'XXXX XXXX XXXX 8908', isDefault: true, category: 'card' },
    { id: '2', type: 'mastercard', logo: 'Mastercard', number: 'XXXX XXXX XXXX 7777', isDefault: false, category: 'card' },
    { id: '3', type: 'paypal', logo: 'PayPal', number: 'XXXX XXXX XXXX 6498', isDefault: false, category: 'card' },
    { id: '4', type: 'mtn', logo: 'MTN MoMo', number: 'MTN Mobile Money', isDefault: false, category: 'momo' },
    { id: '5', type: 'airtel', logo: 'Airtel Money', number: 'Airtel Money', isDefault: false, category: 'momo' },
  ];

  useEffect(() => {
    fetchBookingDetails();
  }, [bookingId]);

  useEffect(() => {
    if (success || isExpired || loading) return;

    if (timeLeft <= 0) {
      setIsExpired(true);
      // Automatically redirect after 5 seconds
      setTimeout(() => navigate('/properties'), 5000);
      return;
    }

    const timerId = setInterval(() => {
      setTimeLeft(prev => prev - 1);
    }, 1000);

    return () => clearInterval(timerId);
  }, [timeLeft, success, isExpired, loading, navigate]);

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

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
          // Show success notification briefly
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
          
          setTimeout(() => setShowNotification(false), 3000); // Just hide the toast, don't redirect
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

  if (isExpired) {
    return (
      <div className="payment-page-wrapper">
        <div className="receipt-card" style={{ textAlign: 'center' }}>
          <AlertCircle size={48} color="#ef4444" style={{ margin: '0 auto 16px' }} />
          <h2>Reservation Session Expired</h2>
          <p style={{ color: '#64748b', marginBottom: '24px' }}>
            You did not complete the payment within the 10-minute window. Your reservation has been released.
          </p>
          <button className="btn-primary" onClick={() => navigate('/properties')} style={{ width: '100%' }}>
            Browse Properties Again
          </button>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="payment-page-wrapper print-wrapper">
        <div className="receipt-card">
          <div className="receipt-header">
            <div className="receipt-logo">
              <CheckCircle size={48} color="#10b981" />
            </div>
            <h2>Payment Receipt</h2>
            <p className="receipt-subtitle">Transaction Successful</p>
          </div>

          <div className="receipt-divider"></div>

          <div className="receipt-body">
            <div className="receipt-row">
              <span className="receipt-label">Property</span>
              <span className="receipt-value">{property?.name || property?.title || booking?.property_name || 'Nestoria Property'}</span>
            </div>
            <div className="receipt-row">
              <span className="receipt-label">Reservation Dates</span>
              <span className="receipt-value">{booking?.start_date} to {booking?.end_date}</span>
            </div>
            <div className="receipt-row">
              <span className="receipt-label">Guests</span>
              <span className="receipt-value">{booking?.number_of_occupants || booking?.number_of_guests || 1}</span>
            </div>
            
            <div className="receipt-divider dashed"></div>
            
            {receipt && (
              <>
                <div className="receipt-row">
                  <span className="receipt-label">Receipt Number</span>
                  <span className="receipt-value monospace">{receipt.receipt_number}</span>
                </div>
                <div className="receipt-row">
                  <span className="receipt-label">Payment ID</span>
                  <span className="receipt-value monospace">{receipt.payment_id}</span>
                </div>
                <div className="receipt-row">
                  <span className="receipt-label">Payment Method</span>
                  <span className="receipt-value capitalize">
                    {mockSavedMethods.find(m => m.id === selectedMethod)?.logo || receipt.payment_method}
                  </span>
                </div>
                <div className="receipt-row">
                  <span className="receipt-label">Date & Time</span>
                  <span className="receipt-value">{new Date(receipt.payment_date).toLocaleString()}</span>
                </div>
              </>
            )}

            <div className="receipt-divider"></div>
            
            <div className="receipt-row receipt-total">
              <span className="receipt-label">Amount Paid</span>
              <span className="receipt-value highlight">UGX {receipt?.amount || booking?.final_amount || booking?.total_amount}</span>
            </div>
          </div>

          <div className="receipt-footer no-print">
            <button className="btn-outline-blue" onClick={() => window.print()}>
               Print Receipt
            </button>
            <button className="btn-primary" onClick={() => navigate('/dashboard')}>
               Return to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="payment-page-wrapper">
      {/* Success Notification */}
      {showNotification && (
        <div className="payment-success-notification">
          <div className="notification-content">
            <div className="notification-icon">✅</div>
            <div className="notification-text">
              <h3>Payment Successful!</h3>
              <p>Your payment has been processed successfully. Reservation confirmed!</p>
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

      {paymentStep === 1 ? (
        <div className="payment-modal">
          <div className="payment-breadcrumb" style={{ display: 'flex', justifyContent: 'space-between' }}>
            <div>Account <span className="arrow">→</span> <span className="current">Payment methods</span></div>
            <div className="payment-timer" style={{ color: timeLeft <= 60 ? '#ef4444' : '#64748b', fontWeight: '600' }}>
              ⏱ {formatTime(timeLeft)}
            </div>
          </div>
          <h1 className="payment-title">Choose your payment method</h1>

          <div className="payment-methods-list">
            {mockSavedMethods.map(method => (
              <div 
                key={method.id} 
                className={`payment-method-card ${selectedMethod === method.id ? 'selected' : ''}`}
                onClick={() => setSelectedMethod(method.id)}
              >
                <div className="method-logo-container">
                  {method.type === 'mastercard' ? (
                    <div className="mc-logo">
                       <div className="mc-red"></div>
                       <div className="mc-orange"></div>
                    </div>
                  ) : method.type === 'paypal' ? (
                     <div className="pp-logo">
                        <span className="p1">P</span><span className="p2">P</span>
                     </div>
                  ) : method.type === 'mtn' ? (
                     <div className="momo-logo mtn-logo">MTN</div>
                  ) : method.type === 'airtel' ? (
                     <div className="momo-logo airtel-logo">airtel</div>
                  ) : (
                    <span className="visa-logo">VISA</span>
                  )}
                </div>
                <div className="method-details">
                  <div className="method-number">{method.number}</div>
                  <div className="method-expiry-default">
                    {method.isDefault && <span className="default-badge">Default</span>}
                  </div>
                </div>
                <div className={`method-check ${selectedMethod === method.id ? 'selected-check' : ''}`}>
                  <CheckCircle className="check-icon" />
                </div>
              </div>
            ))}

            <button 
              className="btn-primary submit-btn-redesign" 
              onClick={() => setPaymentStep(2)}
            >
              Continue
            </button>
          </div>
        </div>
      ) : (
        <div className="payment-container step-2-container">
          <div className="payment-content step-2-content">
            <div className="step-2-left-column">
              <div className="payment-header step-2-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <button onClick={() => setPaymentStep(1)} className="back-btn-step-2">
                    <ArrowLeft size={16} /> Back to payment methods
                  </button>
                  <h2>Enter Payment Details</h2>
                </div>
                <div className="payment-timer" style={{ color: timeLeft <= 60 ? '#ef4444' : '#64748b', fontWeight: '600', padding: '8px 16px', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  ⏱ {formatTime(timeLeft)}
                </div>
              </div>

              <div className="payment-form-section landscape-form-section">
                <div className="reservation-summary light-blue-summary">
                  <div className="summary-title-column">
                    <span>Payment</span>
                    <span>Summary</span>
                  </div>
                  <div className="summary-amount-column">
                    <span className="total-label">Total<br/>Amount<br/>to Pay:</span>
                    <span className="ugx-amount">UGX<br/>{booking?.final_amount || booking?.total_amount || 0}</span>
                  </div>
                </div>

                <form onSubmit={handleSubmit} className="payment-form landscape-form">
                <h3>{mockSavedMethods.find(m => m.id === selectedMethod)?.category === 'momo' ? 'Mobile Money Details' : 'Card Details'}</h3>
                
                {mockSavedMethods.find(m => m.id === selectedMethod)?.category === 'momo' ? (
                  <div className="form-group">
                    <label>Mobile Money Number</label>
                    <input
                      type="tel"
                      name="mobile_money_number"
                      value={mobileMoneyNumber}
                      onChange={(e) => setMobileMoneyNumber(e.target.value)}
                      placeholder="e.g. 077X XXX XXX"
                      required
                    />
                  </div>
                ) : (
                  <>
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
                  </>
                )}

                {error && (
                  <div className="error-message">
                    <AlertCircle />
                    {error}
                  </div>
                )}

                <button 
                  type="submit" 
                  className="btn-outline-blue submit-btn-landscape"
                  disabled={processing}
                >
                  {processing ? (
                    <>
                      <div className="spinner-blue"></div>
                      Processing...
                    </>
                  ) : (
                    <>
                      <div className="circle-outline-icon"></div>
                      <span>Pay UGX<br/>{booking?.final_amount || booking?.total_amount || 0}</span>
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>

          <div className="payment-security step-2-security">
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
      )}
    </div>
  );
};

export default Payment;
