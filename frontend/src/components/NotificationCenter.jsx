import React, { useState, useEffect } from 'react';
import { Bell, X, Check, Settings, Mail, MessageSquare, Calendar, DollarSign, Home, User, AlertCircle, Info } from 'lucide-react';
import api from '../api/axios';
import './NotificationCenter.css';

const NotificationCenter = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [showSettings, setShowSettings] = useState(false);
  const [preferences, setPreferences] = useState({
    email_notifications: true,
    push_notifications: true,
    sms_notifications: false,
    booking_updates: true,
    payment_reminders: true,
    property_alerts: true,
    marketing_emails: false
  });

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      const res = await api.get('/notifications/');
      setNotifications(res.data.results || res.data);
    } catch (error) {
      console.error('Error fetching notifications:', error);
      // Mock data for demonstration
      setNotifications([
        {
          id: 1,
          title: 'Reservation Confirmed',
          message: 'Your reservation for Ocean Breeze Villa has been confirmed. Check-in is on March 20, 2024.',
          type: 'reservation',
          is_read: false,
          created_at: '2 hours ago',
          icon: Calendar
        },
        {
          id: 2,
          title: 'Payment Successful',
          message: 'Your payment of $1,500 for Ocean Breeze Villa has been processed successfully.',
          type: 'payment',
          is_read: false,
          created_at: '4 hours ago',
          icon: DollarSign
        },
        {
          id: 3,
          title: 'New Property Available',
          message: 'A new property matching your search criteria is now available in New York.',
          type: 'property',
          is_read: true,
          created_at: '1 day ago',
          icon: Home
        },
        {
          id: 4,
          title: 'Profile Update',
          message: 'Your profile information has been successfully updated.',
          type: 'system',
          is_read: true,
          created_at: '2 days ago',
          icon: User
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await api.put(`/notifications/${notificationId}/mark-read/`);
      setNotifications(prev =>
        prev.map(notif =>
          notif.id === notificationId ? { ...notif, is_read: true } : notif
        )
      );
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await api.put('/notifications/mark-all-read/');
      setNotifications(prev =>
        prev.map(notif => ({ ...notif, is_read: true }))
      );
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  };

  const deleteNotification = async (notificationId) => {
    try {
      await api.delete(`/notifications/${notificationId}/`);
      setNotifications(prev =>
        prev.filter(notif => notif.id !== notificationId)
      );
    } catch (error) {
      console.error('Error deleting notification:', error);
    }
  };

  const updatePreferences = async (newPreferences) => {
    try {
      await api.put('/notifications/preferences/', newPreferences);
      setPreferences(newPreferences);
    } catch (error) {
      console.error('Error updating preferences:', error);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'reservation':
        return Calendar;
      case 'payment':
        return DollarSign;
      case 'property':
        return Home;
      case 'message':
        return MessageSquare;
      case 'system':
        return Info;
      default:
        return Bell;
    }
  };

  const getNotificationColor = (type) => {
    switch (type) {
      case 'reservation':
        return '#3b82f6';
      case 'payment':
        return '#10b981';
      case 'property':
        return '#8b5cf6';
      case 'message':
        return '#f59e0b';
      case 'system':
        return '#6b7280';
      default:
        return '#6b7280';
    }
  };

  const filteredNotifications = notifications.filter(notif => {
    if (filter === 'all') return true;
    if (filter === 'unread') return !notif.is_read;
    if (filter === 'read') return notif.is_read;
    return notif.type === filter;
  });

  const unreadCount = notifications.filter(n => !n.is_read).length;

  if (loading) {
    return (
      <div className="notification-center">
        <div className="loader">Loading notifications...</div>
      </div>
    );
  }

  return (
    <div className="notification-center">
      <div className="notification-header">
        <div className="header-content">
          <h1>Notification Center</h1>
          <p>
            {unreadCount} unread notification{unreadCount !== 1 ? 's' : ''}
          </p>
        </div>
        <div className="header-actions">
          {unreadCount > 0 && (
            <button className="btn-secondary" onClick={markAllAsRead}>
              <Check /> Mark All Read
            </button>
          )}
          <button
            className="btn-secondary"
            onClick={() => setShowSettings(!showSettings)}
          >
            <Settings /> Settings
          </button>
        </div>
      </div>

      {showSettings && (
        <div className="notification-settings">
          <h3>Notification Preferences</h3>
          <div className="preferences-grid">
            <div className="preference-item">
              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={preferences.email_notifications}
                  onChange={(e) => updatePreferences({
                    ...preferences,
                    email_notifications: e.target.checked
                  })}
                />
                <span className="toggle-slider"></span>
                <div className="preference-info">
                  <Mail />
                  <div>
                    <strong>Email Notifications</strong>
                    <p>Receive notifications via email</p>
                  </div>
                </div>
              </label>
            </div>
            <div className="preference-item">
              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={preferences.push_notifications}
                  onChange={(e) => updatePreferences({
                    ...preferences,
                    push_notifications: e.target.checked
                  })}
                />
                <span className="toggle-slider"></span>
                <div className="preference-info">
                  <Bell />
                  <div>
                    <strong>Push Notifications</strong>
                    <p>Receive browser push notifications</p>
                  </div>
                </div>
              </label>
            </div>
            <div className="preference-item">
              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={preferences.booking_updates}
                  onChange={(e) => updatePreferences({
                    ...preferences,
                    booking_updates: e.target.checked
                  })}
                />
                <span className="toggle-slider"></span>
                <div className="preference-info">
                  <Calendar />
                  <div>
                    <strong>Booking Updates</strong>
                    <p>Updates about your bookings</p>
                  </div>
                </div>
              </label>
            </div>
            <div className="preference-item">
              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={preferences.payment_reminders}
                  onChange={(e) => updatePreferences({
                    ...preferences,
                    payment_reminders: e.target.checked
                  })}
                />
                <span className="toggle-slider"></span>
                <div className="preference-info">
                  <DollarSign />
                  <div>
                    <strong>Payment Reminders</strong>
                    <p>Payment due dates and confirmations</p>
                  </div>
                </div>
              </label>
            </div>
          </div>
        </div>
      )}

      <div className="notification-filters">
        <button
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All ({notifications.length})
        </button>
        <button
          className={`filter-btn ${filter === 'unread' ? 'active' : ''}`}
          onClick={() => setFilter('unread')}
        >
          Unread ({unreadCount})
        </button>
        <button
          className={`filter-btn ${filter === 'read' ? 'active' : ''}`}
          onClick={() => setFilter('read')}
        >
          Read ({notifications.length - unreadCount})
        </button>
        <button
          className={`filter-btn ${filter === 'booking' ? 'active' : ''}`}
          onClick={() => setFilter('booking')}
        >
          Bookings
        </button>
        <button
          className={`filter-btn ${filter === 'payment' ? 'active' : ''}`}
          onClick={() => setFilter('payment')}
        >
          Payments
        </button>
      </div>

      <div className="notifications-list">
        {filteredNotifications.length === 0 ? (
          <div className="empty-notifications">
            <Bell size={48} />
            <h3>No notifications</h3>
            <p>
              {filter === 'all'
                ? "You don't have any notifications yet."
                : `No ${filter} notifications found.`}
            </p>
          </div>
        ) : (
          filteredNotifications.map(notification => {
            const IconComponent = getNotificationIcon(notification.type);
            const iconColor = getNotificationColor(notification.type);
            
            return (
              <div
                key={notification.id}
                className={`notification-item ${!notification.is_read ? 'unread' : ''}`}
              >
                <div className="notification-icon" style={{ color: iconColor }}>
                  <IconComponent size={20} />
                </div>
                <div className="notification-content">
                  <div className="notification-header">
                    <h4>{notification.title}</h4>
                    <span className="notification-time">{notification.created_at}</span>
                  </div>
                  <p>{notification.message}</p>
                </div>
                <div className="notification-actions">
                  {!notification.is_read && (
                    <button
                      className="action-btn"
                      onClick={() => markAsRead(notification.id)}
                      title="Mark as read"
                    >
                      <Check size={16} />
                    </button>
                  )}
                  <button
                    className="action-btn delete"
                    onClick={() => deleteNotification(notification.id)}
                    title="Delete notification"
                  >
                    <X size={16} />
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default NotificationCenter;
