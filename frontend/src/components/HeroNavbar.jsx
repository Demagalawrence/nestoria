import React, { useContext } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Home as HomeIcon, User, PhoneCall, Menu, X, Bell } from 'lucide-react';
import { AuthContext } from '../context/AuthContext';
import './HeroNavbar.css';

const HeroNavbar = () => {
   const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);
   const [isNotificationOpen, setIsNotificationOpen] = React.useState(false);
   const [notifications, setNotifications] = React.useState([
      {
         id: 1,
         title: 'Booking Confirmed',
         message: 'Your booking for Bugema Self-Contained Rooms has been confirmed.',
         time: '2 hours ago',
         read: false,
         type: 'success'
      },
      {
         id: 2,
         title: 'Payment Reminder',
         message: 'Complete your payment for booking #BK2026042411393609E439A8.',
         time: '5 hours ago',
         read: false,
         type: 'warning'
      },
      {
         id: 3,
         title: 'New Property Available',
         message: 'Check out our new luxury apartments in Kampala.',
         time: '1 day ago',
         read: true,
         type: 'info'
      }
   ]);
   const navigate = useNavigate();
   const location = useLocation();
   const { user, logout } = useContext(AuthContext);

   const isHome = location.pathname === '/';
   const isSearch = location.pathname === '/search';
   const isAnalytics = location.pathname === '/analytics';
   const isSupport = location.pathname === '/support';
   const isAbout = location.pathname === '/about';
   const isReservations = location.pathname === '/reservations';

   React.useEffect(() => {
      setIsMobileMenuOpen(false);
   }, [location.pathname]);

   const handleProfileClick = () => {
      if (user) {
         navigate('/dashboard');
      } else {
         navigate('/login');
      }
   };

   const handleNotificationClick = () => {
      setIsNotificationOpen(!isNotificationOpen);
   };

   const handleNotificationItemClick = (notificationId) => {
      // Mark notification as read
      setNotifications(prevNotifications =>
         prevNotifications.map(notification =>
            notification.id === notificationId
               ? { ...notification, read: true }
               : notification
         )
      );
   };

   const getUnreadCount = () => {
      return notifications.filter(notification => !notification.read).length;
   };

   // Close notification dropdown when clicking outside
   React.useEffect(() => {
      const handleClickOutside = (event) => {
         if (isNotificationOpen && !event.target.closest('.notification-bell-container')) {
            setIsNotificationOpen(false);
         }
      };

      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
   }, [isNotificationOpen]);

   return (
      <header className="hero-navbar">
         <div className="navbar-container">
            <div className="navbar-logo">
               <div className="logo-icon-wrapper">
                  <div className="logo-waves"></div>
                  <HomeIcon size={16} className="logo-icon" />
               </div>
               <div className="brand-text">
                  <span className="text-nest">NEST</span><span className="text-tori">TORI</span>
               </div>
            </div>

                        
            <button 
               className="mobile-menu-toggle" 
               onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
               {isMobileMenuOpen ? <X size={24} color="#1D4ED8" /> : <Menu size={24} color="#1D4ED8" />}
            </button>

            <div className={`navbar-menu-overlay ${isMobileMenuOpen ? 'open' : ''}`}>
               <nav className="navbar-nav-links">
               <Link to="/" className={isHome ? 'active' : ''}>Home</Link>
               <span className="nav-dot">·</span>
               <Link to="/search" className={isSearch ? 'active' : ''}>Properties</Link>
               <span className="nav-dot">·</span>
               {user && (
                 <>
                   <Link to="/reservations" className={isReservations ? 'active' : ''}>Reservations</Link>
                   <span className="nav-dot">·</span>
                 </>
               )}
                              {user && (user.role === 'admin' || user.is_verified) && <Link to="/analytics" className={isAnalytics ? 'active' : ''}>Analytics</Link>}
               {user && (user.role === 'admin' || user.is_verified) && <span className="nav-dot">·</span>}
               {user && user.role === 'admin' && <Link to="/admin" className={location.pathname === '/admin' ? 'active' : ''}>Admin Panel</Link>}
               {user && user.role === 'admin' && <span className="nav-dot">·</span>}
               <Link to="/support" className={isSupport ? 'active' : ''}>Support</Link>
               <span className="nav-dot">·</span>
               {(!user || (user.role === 'admin' || user.is_verified)) && <Link to="/about" className={isAbout ? 'active' : ''}>About Us</Link>}
            </nav>

            <div className="navbar-actions">
               <div className="call-anytime">
                  <div className="phone-icon-circle"><PhoneCall size={16} /></div>
                  <div className="call-text">
                     <span>Call Us Anytime</span>
                     <strong>+011 775 643 21</strong>
                  </div>
               </div>
               {user ? (
                  <div className="user-menu">
                     {/* Notification Bell for logged-in users */}
                     <div className="notification-bell-container">
                        <button 
                           className="notification-bell" 
                           title="Notifications"
                           onClick={handleNotificationClick}
                        >
                           <Bell size={20} color="#64748b" />
                           {getUnreadCount() > 0 && (
                              <span className="notification-badge">{getUnreadCount()}</span>
                           )}
                        </button>
                        
                        {/* Notification Dropdown */}
                        {isNotificationOpen && (
                           <div className="notification-dropdown">
                              <div className="notification-header">
                                 <h4>Notifications</h4>
                                 <button 
                                    className="mark-all-read-btn"
                                    onClick={() => setNotifications(prevNotifications =>
                                       prevNotifications.map(notification => ({ ...notification, read: true }))
                                    )}
                                 >
                                    Mark all as read
                                 </button>
                              </div>
                              <div className="notification-list">
                                 {notifications.length > 0 ? (
                                    notifications.map(notification => (
                                       <div
                                          key={notification.id}
                                          className={`notification-item ${!notification.read ? 'unread' : ''}`}
                                          onClick={() => handleNotificationItemClick(notification.id)}
                                       >
                                          <div className="notification-icon">
                                             {notification.type === 'success' && '✅'}
                                             {notification.type === 'warning' && '⚠️'}
                                             {notification.type === 'info' && 'ℹ️'}
                                          </div>
                                          <div className="notification-content">
                                             <div className="notification-title">{notification.title}</div>
                                             <div className="notification-message">{notification.message}</div>
                                             <div className="notification-time">{notification.time}</div>
                                          </div>
                                          {!notification.read && (
                                             <div className="notification-dot"></div>
                                          )}
                                       </div>
                                    ))
                                 ) : (
                                    <div className="no-notifications">
                                       <p>No notifications</p>
                                    </div>
                                 )}
                              </div>
                           </div>
                        )}
                     </div>
                     {user.role === 'admin' ? (
                        <Link to="/admin" className="req-quote-btn">Admin Panel</Link>
                     ) : null}
                     <button onClick={logout} className="req-quote-btn logout-btn">Logout</button>
                  </div>
               ) : (
                  <div className="auth-buttons">
                     <Link to="/login" className="req-quote-btn">Login</Link>
                     <Link to="/register" className="req-quote-btn register-btn">Register</Link>
                  </div>
               )}
            </div>
            </div>
         </div>
      </header>
   );
};

export default HeroNavbar;
