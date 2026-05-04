import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import PropertyDetails from './pages/PropertyDetails'
import Dashboard from './pages/Dashboard'
import AdminDashboard from './pages/AdminDashboard'
import MaintenanceDashboard from './pages/MaintenanceDashboard'
import Booking from './pages/Booking'
import Payment from './pages/Payment'
import PropertyManagement from './pages/PropertyManagement'
import Search from './pages/Search'
import Notifications from './pages/Notifications'
import Reviews from './pages/Reviews'
import Analytics from './pages/Analytics'
import About from './pages/About'
import Support from './pages/Support'
import Location from './pages/Location'
import Reservations from './pages/Reservations'
import TermsOfService from './pages/TermsOfService'
import PrivacyPolicy from './pages/PrivacyPolicy'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import AIChat from './components/AIChat'
import SplashScreen from './components/SplashScreen'
import './App.css'

function App() {
  const [loading, setLoading] = useState(true);

  return (
    <AuthProvider>
      <Router>
        {loading && <SplashScreen finishLoading={() => setLoading(false)} />}
        <div className="global-page-wrapper">
          {/* Clean global wrapper without obsolete shapes */}
          <div className="global-content-wrapper">
            <Navbar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/property/:id" element={<PropertyDetails />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/maintenance" element={<MaintenanceDashboard />} />
            <Route path="/reservations" element={<Reservations />} />
            <Route path="/booking/:id" element={<Booking />} />
            <Route path="/payment/:bookingId" element={<Payment />} />
            <Route path="/property-management" element={<PropertyManagement />} />
            <Route path="/search" element={<Search />} />
            <Route path="/notifications" element={<Notifications />} />
            <Route path="/reviews/:propertyId" element={<Reviews />} />
            <Route path="/analytics" element={<Analytics />} />
                        <Route path="/about" element={<About />} />
            <Route path="/location" element={<Location />} />
            <Route path="/support" element={<Support />} />
            <Route path="/terms" element={<TermsOfService />} />
            <Route path="/privacy" element={<PrivacyPolicy />} />
          </Routes>
          <Footer />
          </div>
        </div>
        <AIChat />
      </Router>
    </AuthProvider>
  );
}

export default App
