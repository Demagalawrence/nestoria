import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Edit, Trash2, Eye, Home, MapPin, Bed, Bath, DollarSign, Calendar, Image, Video, X, Upload, Check } from 'lucide-react';
import api from '../api/axios';
import './PropertyManagement.css';

const PropertyManagement = () => {
  const navigate = useNavigate();
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingProperty, setEditingProperty] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    location: '',
    price: '',
    bedrooms: '',
    bathrooms: '',
    property_type: 'apartment',
    contact_number: '',
    whatsapp_number: '',
    contact_person: '',
    amenities: '',
    address: '',
    city: '',
    country: '',
    postal_code: ''
  });
  const [imageFiles, setImageFiles] = useState([]);
  const [videoFiles, setVideoFiles] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    fetchProperties();
  }, []);

  const fetchProperties = async () => {
    try {
      const res = await api.get('/properties/');
      setProperties(res.data.results || res.data);
    } catch (error) {
      console.error('Error fetching properties:', error);
      setError('Could not load your properties');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleImageUpload = (e) => {
    setImageFiles(Array.from(e.target.files));
  };

  const handleVideoUpload = (e) => {
    setVideoFiles(Array.from(e.target.files));
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      location: '',
      price: '',
      bedrooms: '',
      bathrooms: '',
      property_type: 'apartment',
      contact_number: '',
      whatsapp_number: '',
      contact_person: '',
      amenities: '',
      address: '',
      city: '',
      country: '',
      postal_code: ''
    });
    setImageFiles([]);
    setVideoFiles([]);
    setEditingProperty(null);
  };

  const openModal = (property = null) => {
    if (property) {
      setEditingProperty(property);
      setFormData({
        title: property.title || '',
        description: property.description || '',
        location: property.location || '',
        price: property.price || '',
        bedrooms: property.bedrooms || '',
        bathrooms: property.bathrooms || '',
        property_type: property.property_type || 'apartment',
        contact_number: property.contact_number || '',
        whatsapp_number: property.whatsapp_number || '',
        contact_person: property.contact_person || '',
        amenities: property.amenities || '',
        address: property.address || '',
        city: property.city || '',
        country: property.country || '',
        postal_code: property.postal_code || ''
      });
    } else {
      resetForm();
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    resetForm();
    setError(null);
    setSuccess(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    setSuccess(null);

    try {
      const data = new FormData();
      
      // Add form fields
      Object.keys(formData).forEach(key => {
        if (formData[key]) {
          data.append(key, formData[key]);
        }
      });

      // Add images
      imageFiles.forEach((file, index) => {
        data.append(`image_${index}`, file);
      });

      // Add videos
      videoFiles.forEach((file, index) => {
        data.append(`video_${index}`, file);
      });

      let res;
      if (editingProperty) {
        res = await api.put(`/properties/${editingProperty.id}/update/`, data, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
      } else {
        res = await api.post('/properties/create/', data, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
      }

      if (res.data.id) {
        setSuccess(editingProperty ? 'Property updated successfully!' : 'Property created successfully!');
        fetchProperties();
        setTimeout(() => {
          closeModal();
        }, 2000);
      }
    } catch (error) {
      console.error('Error saving property:', error);
      setError(error.response?.data?.message || 'Failed to save property. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (propertyId) => {
    if (window.confirm('Are you sure you want to delete this property?')) {
      try {
        await api.delete(`/properties/${propertyId}/delete/`);
        setProperties(prev => prev.filter(p => p.id !== propertyId));
        setSuccess('Property deleted successfully!');
        setTimeout(() => setSuccess(null), 3000);
      } catch (error) {
        console.error('Error deleting property:', error);
        setError('Failed to delete property. Please try again.');
      }
    }
  };

  if (loading) {
    return (
      <div className="property-management-container">
        <div className="loader">Loading your properties...</div>
      </div>
    );
  }

  return (
    <div className="property-management-container">
      <div className="management-header">
        <div className="header-content">
          <h1>Property Management</h1>
          <p>Manage your property listings and bookings</p>
        </div>
        <button className="btn-primary" onClick={() => openModal()}>
          <Plus /> Add New Property
        </button>
      </div>

      {error && (
        <div className="error-message">{error}</div>
      )}

      {success && (
        <div className="success-message">{success}</div>
      )}

      <div className="properties-grid">
        {properties.length === 0 ? (
          <div className="empty-state">
            <Home />
            <h3>No Properties Yet</h3>
            <p>Start by adding your first property to begin receiving bookings.</p>
            <button className="btn-primary" onClick={() => openModal()}>
              <Plus /> Add Your First Property
            </button>
          </div>
        ) : (
          properties.map(property => (
            <div key={property.id} className="property-card">
              <div className="property-image">
                {property.image || property.image_url ? (
                  <img src={property.image || property.image_url} alt={property.title} />
                ) : (
                  <div className="no-image">
                    <Home />
                  </div>
                )}
              </div>
              
              <div className="property-content">
                <div className="property-header">
                  <h3>{property.title}</h3>
                  <span className={`status ${property.status || 'active'}`}>
                    {property.status || 'Active'}
                  </span>
                </div>
                
                <div className="property-location">
                  <MapPin size={16} />
                  <span>{property.location || property.address}</span>
                </div>
                
                <div className="property-features">
                  <span><Bed size={16} /> {property.bedrooms || 0} Beds</span>
                  <span><Bath size={16} /> {property.bathrooms || 0} Baths</span>
                  <span><Home size={16} /> {property.property_type || 'Property'}</span>
                </div>
                
                <div className="property-price">
                  <DollarSign size={16} />
                  <span>UGX {property.price || 0}/month</span>
                </div>
                
                <div className="property-actions">
                  <button 
                    className="btn-secondary" 
                    onClick={() => navigate(`/property/${property.id}`)}
                  >
                    <Eye /> View
                  </button>
                  <button 
                    className="btn-secondary" 
                    onClick={() => openModal(property)}
                  >
                    <Edit /> Edit
                  </button>
                  <button 
                    className="btn-danger" 
                    onClick={() => handleDelete(property.id)}
                  >
                    <Trash2 /> Delete
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>{editingProperty ? 'Edit Property' : 'Add New Property'}</h2>
              <button className="close-btn" onClick={closeModal}>
                <X />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="property-form">
              <div className="form-sections">
                <div className="form-section">
                  <h3>Basic Information</h3>
                  <div className="form-grid">
                    <div className="form-group">
                      <label>Property Title *</label>
                      <input
                        type="text"
                        name="title"
                        value={formData.title}
                        onChange={handleInputChange}
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label>Property Type *</label>
                      <select
                        name="property_type"
                        value={formData.property_type}
                        onChange={handleInputChange}
                        required
                      >
                        <option value="apartment">Apartment</option>
                        <option value="house">House</option>
                        <option value="villa">Villa</option>
                        <option value="studio">Studio</option>
                        <option value="hostel">Hostel</option>
                        <option value="bedsitter">Bedsitter</option>
                        <option value="single_room">Single Room</option>
                        <option value="double_room">Double Room</option>
                        <option value="self_contained">Self Contained</option>
                        <option value="boys_quarters">Boys' Quarters</option>
                        <option value="servants_quarters">Servants' Quarters</option>
                        <option value="flat">Flat</option>
                        <option value="shared_room">Shared Room</option>
                        <option value="commercial">Commercial Space</option>
                        <option value="office">Office Space</option>
                      </select>
                    </div>
                    <div className="form-group full-width">
                      <label>Description *</label>
                      <textarea
                        name="description"
                        value={formData.description}
                        onChange={handleInputChange}
                        rows={4}
                        required
                      />
                    </div>
                  </div>
                </div>

                <div className="form-section">
                  <h3>Location</h3>
                  <div className="form-grid">
                    <div className="form-group">
                      <label>Address *</label>
                      <input
                        type="text"
                        name="address"
                        value={formData.address}
                        onChange={handleInputChange}
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label>District *</label>
                      <input
                        type="text"
                        name="district"
                        value={formData.district || ''}
                        onChange={handleInputChange}
                        placeholder="e.g., Kampala, Wakiso, Mukono"
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label>County</label>
                      <input
                        type="text"
                        name="county"
                        value={formData.county || ''}
                        onChange={handleInputChange}
                        placeholder="e.g., Kyadondo"
                      />
                    </div>
                    <div className="form-group">
                      <label>Sub-County</label>
                      <input
                        type="text"
                        name="sub_county"
                        value={formData.sub_county || ''}
                        onChange={handleInputChange}
                        placeholder="e.g., Central, Kawempe"
                      />
                    </div>
                    <div className="form-group">
                      <label>Parish</label>
                      <input
                        type="text"
                        name="parish"
                        value={formData.parish || ''}
                        onChange={handleInputChange}
                        placeholder="e.g., Makerere"
                      />
                    </div>
                    <div className="form-group">
                      <label>Village/Locality</label>
                      <input
                        type="text"
                        name="village"
                        value={formData.village || ''}
                        onChange={handleInputChange}
                        placeholder="e.g., Kikoni, Katwe"
                      />
                    </div>
                  </div>
                </div>

                <div className="form-section">
                  <h3>Property Details</h3>
                  <div className="form-grid">
                    <div className="form-group">
                      <label>Price per Month (UGX) *</label>
                      <input
                        type="number"
                        name="price"
                        value={formData.price}
                        onChange={handleInputChange}
                        min="0"
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label>Bedrooms *</label>
                      <input
                        type="number"
                        name="bedrooms"
                        value={formData.bedrooms}
                        onChange={handleInputChange}
                        min="0"
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label>Bathrooms *</label>
                      <input
                        type="number"
                        name="bathrooms"
                        value={formData.bathrooms}
                        onChange={handleInputChange}
                        min="0"
                        required
                      />
                    </div>
                    <div className="form-group full-width">
                      <label>Amenities</label>
                      <textarea
                        name="amenities"
                        value={formData.amenities}
                        onChange={handleInputChange}
                        placeholder="WiFi, Parking, Generator, Solar Power, Water Tank, Security, Borehole, etc."
                        rows={3}
                      />
                    </div>
                  </div>
                </div>

                <div className="form-section">
                  <h3>Contact Information</h3>
                  <div className="form-grid">
                    <div className="form-group">
                      <label>Contact Person *</label>
                      <input
                        type="text"
                        name="contact_person"
                        value={formData.contact_person}
                        onChange={handleInputChange}
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label>Phone Number *</label>
                      <input
                        type="tel"
                        name="contact_number"
                        value={formData.contact_number}
                        onChange={handleInputChange}
                        placeholder="+256 7XX XXX XXX"
                        pattern="\+256[ -]?\d{3}[ -]?\d{3}[ -]?\d{3}"
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label>WhatsApp Number</label>
                      <input
                        type="tel"
                        name="whatsapp_number"
                        value={formData.whatsapp_number}
                        onChange={handleInputChange}
                        placeholder="+256 7XX XXX XXX"
                        pattern="\+256[ -]?\d{3}[ -]?\d{3}[ -]?\d{3}"
                      />
                    </div>
                  </div>
                </div>

                <div className="form-section">
                  <h3>Media</h3>
                  <div className="form-grid">
                    <div className="form-group">
                      <label>Property Images</label>
                      <div className="file-upload">
                        <input
                          type="file"
                          multiple
                          accept="image/*"
                          onChange={handleImageUpload}
                          id="images"
                        />
                        <label htmlFor="images" className="file-label">
                          <Upload />
                          <span>Choose Images</span>
                        </label>
                        {imageFiles.length > 0 && (
                          <div className="file-list">
                            {imageFiles.map((file, index) => (
                              <span key={index} className="file-item">
                                {file.name}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="form-group">
                      <label>Property Videos</label>
                      <div className="file-upload">
                        <input
                          type="file"
                          multiple
                          accept="video/*"
                          onChange={handleVideoUpload}
                          id="videos"
                        />
                        <label htmlFor="videos" className="file-label">
                          <Video />
                          <span>Choose Videos</span>
                        </label>
                        {videoFiles.length > 0 && (
                          <div className="file-list">
                            {videoFiles.map((file, index) => (
                              <span key={index} className="file-item">
                                {file.name}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="form-actions">
                <button type="button" className="btn-secondary" onClick={closeModal}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={submitting}>
                  {submitting ? (
                    <>
                      <div className="spinner"></div>
                      {editingProperty ? 'Updating...' : 'Creating...'}
                    </>
                  ) : (
                    <>
                      <Check />
                      {editingProperty ? 'Update Property' : 'Create Property'}
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default PropertyManagement;
