import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { MapPin, Bed, Bath, User, MessageCircle, Phone, Star, Headphones, ArrowLeft } from 'lucide-react';
import api from '../api/axios';
import AgentRequestForm from '../components/AgentRequestForm';
import './PropertyDetails.css';

const PropertyDetails = () => {
  const { id } = useParams();
  const [property, setProperty] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAgentForm, setShowAgentForm] = useState(false);
  const [availableRooms, setAvailableRooms] = useState([]);
  const [roomsLoading, setRoomsLoading] = useState(true);

  useEffect(() => {
    // Scroll to top when loaded
    window.scrollTo(0, 0);
    
    const fetchPropertyData = async () => {
      try {
        const res = await api.get(`/properties/${id}/`);
        setProperty(res.data);
        
        try {
          const roomsRes = await api.get(`/api/properties/${id}/rooms/`);
          if (Array.isArray(roomsRes.data)) {
            const vacantRooms = roomsRes.data.filter(room => room.status === 'vacant' && room.available_beds > 0);
            setAvailableRooms(vacantRooms);
          }
        } catch (roomsErr) {
          console.error("Error fetching rooms:", roomsErr);
        }
      } catch (err) {
        console.error("Error fetching property:", err);
        setError("Could not load property details.");
        
        // Fallback for UI visualization if backend is unavailable
        setProperty({
          id,
          title: 'Ocean Breeze Villa',
          description: 'A beautiful modern villa with ocean views, spacious living areas, high-end finishing, and an outdoor pool. Perfect for a luxury lifestyle and relaxing vacations. The property boasts a massive 5000 sq ft lot, an infinity pool, and a private driveway.',
          location: '123 Main Street, Anytown',
          price: 910000,
          bedrooms: 4,
          bathrooms: 2,
          contact_number: '+1234567890',
          whatsapp_number: '+1234567890',
          contact_person: 'John Doe',
          image_url: 'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?ixlib=rb-4.0.3&auto=format&fit=crop&w=1600&q=80',
          property_type: 'Villa'
        });
      } finally {
        setLoading(false);
        setRoomsLoading(false);
      }
    };
    fetchPropertyData();
  }, [id]);

  if (loading) return <div className="loader container mt-nav">Loading property details...</div>;
  if (error && !property) return <div className="error-message container mt-nav">{error}</div>;

  const handleWhatsApp = () => {
    if (property.whatsapp_number) {
      const message = encodeURIComponent(`Hi, I am interested in ${property.title}`);
      window.open(`https://wa.me/${property.whatsapp_number.replace(/\D/g, '')}?text=${message}`, '_blank');
    }
  };

  const handleCall = () => {
    if (property.contact_number) {
      window.open(`tel:${property.contact_number}`, '_self');
    }
  };

  const heroImage = property.images?.[0]?.image || property.primary_image?.image || property.image_url || property.image;

  return (
    <div className="property-details-page">
      {/* Premium Dark Gradient Header (Matches Contact Page) */}
      <div className="inner-page-hero property-header-hero">
        <div className="container hero-content-wrapper" style={{textAlign: 'left'}}>
          <Link to="/" className="back-link-white"><ArrowLeft size={18} /> Back to listings</Link>
          <h1 className="inner-hero-title">{property.title || property.name}</h1>
          <p className="inner-hero-subtitle" style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
            <MapPin size={20} /> {property.location || property.address || property.full_address || property.address_line_1}
          </p>
        </div>
      </div>

      <div className="container property-main-container">
        
        {/* Main Image Gallery Card */}
        <div className="property-gallery-card">
          <img src={heroImage} alt={property.title || 'Property'} className="property-main-image" />
        </div>

        <div className="property-content-grid">
          <div className="property-info-main">
            
            <div className="property-price-card">
              <div className="price-label">Monthly Rent</div>
              <div className="detail-price">UGX {Number(property.price || property.rent_per_month || 0).toLocaleString('en-US')}</div>
            </div>

            <div className="detail-features">
              <div className="feature-item">
                <span className="feature-value">{property.bedrooms || property.rooms || 0}</span>
                <span className="feature-label"><Bed size={20} /> Bedrooms</span>
              </div>
              <div className="feature-item">
                <span className="feature-value">{property.bathrooms || 0}</span>
                <span className="feature-label"><Bath size={20} /> Bathrooms</span>
              </div>
              <div className="feature-item">
                <span className="feature-value">{property.property_type || 'Property'}</span>
                <span className="feature-label">Property Type</span>
              </div>
            </div>
            
            <div className="property-description">
              <h3>About this property</h3>
              <p>{property.description || 'No description provided.'}</p>
            </div>
          </div>
          
          <div className="property-sidebar">
            <div className="contact-card sticky-card">
              <h3>Contact Agent</h3>
              <div className="agent-info">
                <div className="agent-avatar"><User size={24} color="#10B981" /></div>
                <div className="agent-details">
                  <span className="agent-name">{property.contact_person || 'Agent'}</span>
                  <span className="agent-role">Property Manager</span>
                </div>
              </div>
              
              <div className="contact-actions">
                <button 
                  onClick={() => setShowAgentForm(true)} 
                  className="contact-btn agent-btn"
                >
                  <Headphones size={18} /> Connect with Agent
                </button>
                <button 
                  onClick={handleWhatsApp} 
                  className="contact-btn whatsapp-btn"
                  disabled={!property.whatsapp_number}
                >
                  <MessageCircle size={18} /> WhatsApp
                </button>
                <button 
                  onClick={handleCall} 
                  className="contact-btn call-btn"
                  disabled={!property.contact_number}
                >
                  <Phone size={18} /> Call
                </button>
              </div>
              
              <div className="action-divider"></div>
              
              {!roomsLoading && (
                <div style={{marginBottom: '15px', textAlign: 'center'}}>
                  {availableRooms.length > 0 ? (
                    <div style={{color: '#28a745', fontWeight: 'bold'}}>
                      {availableRooms.length}/10 Rooms Available
                    </div>
                  ) : (
                    <div style={{color: '#dc3545', fontWeight: 'bold', padding: '10px', backgroundColor: '#fff8f8', borderRadius: '5px', border: '1px solid #dc3545'}}>
                      Hostel is Full
                    </div>
                  )}
                </div>
              )}
              
              {availableRooms.length === 0 && !roomsLoading ? (
                <button className="book-btn" disabled style={{backgroundColor: '#ccc', cursor: 'not-allowed', width: '100%'}}>
                  Hostel is Full
                </button>
              ) : (
                <Link to={`/booking/${property.id}`} className="book-btn">
                  Reserve this Property
                </Link>
              )}
              
              <Link to={`/reviews/${property.id}`} className="reviews-btn">
                <Star size={16} /> Read Reviews
              </Link>
            </div>
          </div>
        </div>
      </div>
      
      {/* Agent Request Form Modal */}
      {showAgentForm && (
        <AgentRequestForm
          property={property}
          onClose={() => setShowAgentForm(false)}
          onSuccess={() => {
            setShowAgentForm(false);
            alert('Agent request submitted successfully! An agent will contact you soon.');
          }}
        />
      )}
    </div>
  );
};

export default PropertyDetails;
