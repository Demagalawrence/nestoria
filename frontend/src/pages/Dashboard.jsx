import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { User, Calendar, CreditCard, Bell, Settings, LogOut, Home, MessageCircle, Star, Building, BarChart3 } from 'lucide-react';
import api from '../api/axios';
import './Dashboard.css';

const Dashboard = () => {
  const [bookings, setBookings] = useState([]);
  const [payments, setPayments] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [user, setUser] = useState(null);
  const [selectedReceipt, setSelectedReceipt] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const userRes = await api.get('/accounts/profile/');
      setUser(userRes.data);
      
      // Fetch regular user data (admin can also view this)
      const [bookingsRes, paymentsRes, notificationsRes] = await Promise.all([
        api.get('/bookings/'),
        api.get('/payments/'),
        api.get('/notifications/')
      ]);
      
      setBookings(bookingsRes.data?.results || []);
      setPayments(paymentsRes.data?.results || []);
      setNotifications(notificationsRes.data?.results || []);
    } catch (error) {
      console.error('Error fetching user data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.role === 'admin') {
      navigate('/admin');
    }
  }, [user, navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const handleViewReceipt = async (paymentId) => {
    try {
      const receiptRes = await api.get(`/payments/receipt/${paymentId}/`);
      setSelectedReceipt(receiptRes.data);
    } catch (error) {
      console.error('Error fetching receipt:', error);
    }
  };

  const closeReceiptModal = () => {
    setSelectedReceipt(null);
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loader">Loading dashboard...</div>
      </div>
    );
  }

  // Admin view indicator
  const isAdminView = user?.role === 'admin';

  const renderOverview = () => (
    <div className="dashboard-grid">
      <div className="stat-card">
        <div className="stat-icon">
          <Calendar />
        </div>
        <div className="stat-content">
          <h3>{bookings.length}</h3>
          <p>Total Bookings</p>
        </div>
      </div>
      <div className="stat-card">
        <div className="stat-icon">
          <CreditCard />
        </div>
        <div className="stat-content">
          <h3>{payments.length}</h3>
          <p>Payments</p>
        </div>
      </div>
      <div className="stat-card">
        <div className="stat-icon">
          <Bell />
        </div>
        <div className="stat-content">
          <h3>{notifications.filter(n => !n.is_read).length}</h3>
          <p>Unread</p>
        </div>
      </div>
      <div className="stat-card">
        <div className="stat-icon">
          <Star />
        </div>
        <div className="stat-content">
          <h3>4.8</h3>
          <p>Avg Rating</p>
        </div>
      </div>
    </div>
  );

  const renderBookings = () => (
    <div className="bookings-section">
      <h3>My Bookings</h3>
      {bookings.length === 0 ? (
        <p className="no-data">No bookings found</p>
      ) : (
        <div className="bookings-list">
          {bookings.map(booking => (
            <div key={booking.id} className="booking-card">
              <div className="booking-info">
                <h4>{booking.property_title || 'Property Booking'}</h4>
                <p><strong>Check-in:</strong> {booking.check_in_date || 'Not set'}</p>
                <p><strong>Check-out:</strong> {booking.check_out_date || 'Not set'}</p>
                <p><strong>Status:</strong> <span className={`status ${booking.status}`}>{booking.status}</span></p>
              </div>
              <div className="booking-actions">
                <button className="btn-secondary">View Details</button>
                {booking.status === 'pending' && (
                  <button className="btn-danger">Cancel</button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderPayments = () => (
    <div className="payments-section">
      <h3>Payment History</h3>
      {payments.length === 0 ? (
        <p className="no-data">No payments found</p>
      ) : (
        <div className="payments-list">
          {payments.map(payment => (
            <div key={payment.id} className="payment-card">
              <div className="payment-info">
                <h4>Payment #{payment.id}</h4>
                <p><strong>Amount:</strong> UGX {payment.amount || '0'}</p>
                <p><strong>Date:</strong> {payment.created_at || 'Not set'}</p>
                <p><strong>Status:</strong> <span className={`status ${payment.status}`}>{payment.status}</span></p>
              </div>
              <div className="payment-actions">
                <button className="btn-secondary" onClick={() => handleViewReceipt(payment.id)}>View Receipt</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderNotifications = () => (
    <div className="notifications-section">
      <h3>Notifications</h3>
      {notifications.length === 0 ? (
        <p className="no-data">No notifications</p>
      ) : (
        <div className="notifications-list">
          {notifications.map(notification => (
            <div key={notification.id} className={`notification-card ${!notification.is_read ? 'unread' : ''}`}>
              <div className="notification-content">
                <h4>{notification.title || 'Notification'}</h4>
                <p>{notification.message || 'No message'}</p>
                <p className="notification-time">{notification.created_at || 'Just now'}</p>
              </div>
              <div className="notification-actions">
                {!notification.is_read && (
                  <button className="btn-secondary">Mark as Read</button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderProfile = () => (
    <div className="profile-section">
      <h3>Profile Information</h3>
      {user && (
        <div className="profile-card">
          <div className="profile-header">
            <div className="profile-avatar">
              <User />
            </div>
            <div className="profile-info">
              <h4>{user.first_name && user.last_name ? `${user.first_name} ${user.last_name}` : user.email}</h4>
              <p>{user.email}</p>
              <p><strong>Role:</strong> {user.role || 'User'}</p>
            </div>
          </div>
          <div className="profile-details">
            <div className="detail-group">
              <label>First Name</label>
              <input type="text" value={user.first_name || ''} readOnly />
            </div>
            <div className="detail-group">
              <label>Last Name</label>
              <input type="text" value={user.last_name || ''} readOnly />
            </div>
            <div className="detail-group">
              <label>Phone Number</label>
              <input type="tel" value={user.phone_number || ''} readOnly />
            </div>
            <div className="detail-group">
              <label>Address</label>
              <input type="text" value={user.address || ''} readOnly />
            </div>
          </div>
          <button className="btn-primary">Edit Profile</button>
        </div>
      )}
    </div>
  );

  return (
    <div className="dashboard-container">
      <div className="dashboard-sidebar">
        <div className="sidebar-header">
          <div className="user-info">
            <div className="user-avatar">
              <User />
            </div>
            <div className="user-details">
              <h4>{user?.first_name && user?.last_name ? `${user.first_name} ${user.last_name}` : user?.email}</h4>
              <p>{user?.role || 'User'}</p>
            </div>
          </div>
        </div>
        <nav className="sidebar-nav">
          <button 
            className={`nav-item ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            <Home /> Overview
          </button>
          <button 
            className={`nav-item ${activeTab === 'bookings' ? 'active' : ''}`}
            onClick={() => setActiveTab('bookings')}
          >
            <Calendar /> My Bookings
          </button>
          <button 
            className={`nav-item ${activeTab === 'payments' ? 'active' : ''}`}
            onClick={() => setActiveTab('payments')}
          >
            <CreditCard /> Payments
          </button>
          <button 
            className={`nav-item ${activeTab === 'notifications' ? 'active' : ''}`}
            onClick={() => navigate('/notifications')}
          >
            <Bell /> Notifications
          </button>
          {(user?.role === 'owner' || user?.role === 'admin') && (
            <>
              <Link to="/property-management" className="nav-item">
                <Building /> Property Management
              </Link>
              <Link to="/analytics" className="nav-item">
                <BarChart3 /> Analytics
              </Link>
            </>
          )}
          <button 
            className={`nav-item ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            <User /> Profile
          </button>
          <button 
            className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            <Settings /> Settings
          </button>
        </nav>
        <div className="sidebar-footer">
          <button className="logout-btn" onClick={handleLogout}>
            <LogOut /> Logout
          </button>
        </div>
      </div>

      <div className="dashboard-main">
        <div className="dashboard-header">
          <div>
            <h1>Client Dashboard</h1>
            {isAdminView && (
              <p style={{ color: '#1a656e', fontSize: '14px', marginTop: '4px' }}>
                👁️ Viewing as client - <Link to="/admin" style={{ color: '#1a656e', textDecoration: 'underline' }}>Go to Admin Panel</Link>
              </p>
            )}
          </div>
          <div className="header-actions">
            <button className="btn-primary" onClick={() => navigate('/')}>
              Browse Properties
            </button>
            {isAdminView && (
              <button className="btn-secondary" onClick={() => navigate('/admin')} style={{ marginLeft: '10px' }}>
                Admin Panel
              </button>
            )}
          </div>
        </div>

        <div className="dashboard-content">
          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'bookings' && renderBookings()}
          {activeTab === 'payments' && renderPayments()}
          {activeTab === 'notifications' && renderNotifications()}
          {activeTab === 'profile' && renderProfile()}
          {activeTab === 'settings' && (
            <div className="settings-section">
              <h3>Settings</h3>
              <p>Settings functionality coming soon...</p>
            </div>
          )}
        </div>
      </div>

      {/* Receipt Modal */}
      {selectedReceipt && (
        <div className="receipt-modal-overlay" onClick={closeReceiptModal}>
          <div className="receipt-modal" onClick={(e) => e.stopPropagation()}>
            <div className="receipt-modal-header">
              <h3>Payment Receipt</h3>
              <button className="close-btn" onClick={closeReceiptModal}>×</button>
            </div>
            <div className="receipt-modal-content">
              <div className="receipt-info">
                <div className="receipt-row">
                  <span>Receipt Number:</span>
                  <span>{selectedReceipt.receipt_number}</span>
                </div>
                <div className="receipt-row">
                  <span>Payment ID:</span>
                  <span>{selectedReceipt.payment_id}</span>
                </div>
                <div className="receipt-row">
                  <span>Amount Paid:</span>
                  <span>${selectedReceipt.amount}</span>
                </div>
                <div className="receipt-row">
                  <span>Payment Method:</span>
                  <span>{selectedReceipt.payment_method}</span>
                </div>
                <div className="receipt-row">
                  <span>Payment Date:</span>
                  <span>{new Date(selectedReceipt.payment_date).toLocaleString()}</span>
                </div>
                <div className="receipt-row">
                  <span>Booking Status:</span>
                  <span className="status-confirmed">Confirmed</span>
                </div>
              </div>
              <div className="receipt-actions">
                <button className="btn-primary" onClick={() => window.print()}>
                  Print Receipt
                </button>
                <button className="btn-secondary" onClick={closeReceiptModal}>
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
