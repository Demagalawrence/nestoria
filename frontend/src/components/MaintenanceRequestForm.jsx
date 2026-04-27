import React, { useState, useEffect } from 'react';
import { 
  X, Camera, Paperclip, AlertCircle, Clock, MapPin, 
  DollarSign, User, Calendar, CheckSquare
} from 'lucide-react';
import maintenanceService from '../services/maintenanceService';
import './MaintenanceRequestForm.css';

const MaintenanceRequestForm = ({ 
  property, 
  room, 
  onClose, 
  onSuccess, 
  editMode = false,
  initialData = null 
}) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    priority: 'medium',
    property: property?.id || '',
    room: room?.id || '',
    preferred_date: '',
    access_instructions: '',
    permission_to_enter: false,
    tenant_present: false,
    estimated_cost: ''
  });

  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [images, setImages] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);

  useEffect(() => {
    fetchCategories();
    if (editMode && initialData) {
      setFormData({
        ...formData,
        ...initialData,
        property: initialData.property?.id || '',
        room: initialData.room?.id || ''
      });
    }
  }, [editMode, initialData, property, room]);

  const fetchCategories = async () => {
    try {
      const response = await maintenanceService.getCategories();
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleImageChange = (e) => {
    const files = Array.from(e.target.files);
    const newImages = [...images, ...files];
    setImages(newImages);

    // Create previews
    files.forEach(file => {
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreviews(prev => [...prev, e.target.result]);
      };
      reader.readAsDataURL(file);
    });
  };

  const removeImage = (index) => {
    const newImages = images.filter((_, i) => i !== index);
    const newPreviews = imagePreviews.filter((_, i) => i !== index);
    setImages(newImages);
    setImagePreviews(newPreviews);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Create maintenance request
      const submitData = new FormData();
      Object.keys(formData).forEach(key => {
        if (formData[key] !== '' && formData[key] !== null) {
          submitData.append(key, formData[key]);
        }
      });

      // Add images
      images.forEach(image => {
        submitData.append('images', image);
      });

      if (editMode) {
        await maintenanceService.updateRequest(initialData.id, submitData);
      } else {
        await maintenanceService.createRequest(submitData);
      }

      onSuccess();
      onClose();
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to submit request');
    } finally {
      setLoading(false);
    }
  };

  const getPriorityIcon = (priority) => {
    const icons = {
      urgent: <AlertCircle size={16} />,
      high: <AlertCircle size={16} />,
      medium: <Clock size={16} />,
      low: <Clock size={16} />
    };
    return icons[priority] || <Clock size={16} />;
  };

  return (
    <div className="maintenance-request-form-overlay">
      <div className="maintenance-request-form">
        <div className="form-header">
          <h2>{editMode ? 'Edit Request' : 'Create Maintenance Request'}</h2>
          <button onClick={onClose} className="close-btn">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="form-content">
          {error && (
            <div className="error-message">
              <AlertCircle size={16} />
              {error}
            </div>
          )}

          {/* Basic Information */}
          <div className="form-section">
            <h3>Basic Information</h3>
            
            <div className="form-group">
              <label>Title *</label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="Brief description of the issue"
                required
              />
            </div>

            <div className="form-group">
              <label>Description *</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Detailed description of the maintenance issue"
                rows={4}
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Category *</label>
                <select
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select category</option>
                  {categories.map(category => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Priority *</label>
                <select
                  name="priority"
                  value={formData.priority}
                  onChange={handleChange}
                  required
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
            </div>
          </div>

          {/* Location */}
          <div className="form-section">
            <h3>Location</h3>
            
            <div className="form-row">
              <div className="form-group">
                <label>Property *</label>
                <input
                  type="text"
                  value={property?.name || ''}
                  disabled
                  className="disabled-input"
                />
              </div>

              {room && (
                <div className="form-group">
                  <label>Room</label>
                  <input
                    type="text"
                    value={room.room_number || ''}
                    disabled
                    className="disabled-input"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Scheduling */}
          <div className="form-section">
            <h3>Scheduling</h3>
            
            <div className="form-row">
              <div className="form-group">
                <label>Preferred Date</label>
                <input
                  type="datetime-local"
                  name="preferred_date"
                  value={formData.preferred_date}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label>Estimated Cost</label>
                <div className="input-with-icon">
                  <DollarSign size={16} />
                  <input
                    type="number"
                    name="estimated_cost"
                    value={formData.estimated_cost}
                    onChange={handleChange}
                    placeholder="0.00"
                    step="0.01"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Access Information */}
          <div className="form-section">
            <h3>Access Information</h3>
            
            <div className="form-group">
              <label>Access Instructions</label>
              <textarea
                name="access_instructions"
                value={formData.access_instructions}
                onChange={handleChange}
                placeholder="How can maintenance staff access the property?"
                rows={2}
              />
            </div>

            <div className="checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="permission_to_enter"
                  checked={formData.permission_to_enter}
                  onChange={handleChange}
                />
                <span className="checkmark"></span>
                Permission to enter when not present
              </label>

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="tenant_present"
                  checked={formData.tenant_present}
                  onChange={handleChange}
                />
                <span className="checkmark"></span>
                Must be present during maintenance
              </label>
            </div>
          </div>

          {/* Images */}
          <div className="form-section">
            <h3>Photos</h3>
            
            <div className="image-upload-area">
              <input
                type="file"
                id="images"
                multiple
                accept="image/*"
                onChange={handleImageChange}
                style={{ display: 'none' }}
              />
              <label htmlFor="images" className="upload-btn">
                <Camera size={20} />
                Add Photos
              </label>
            </div>

            {imagePreviews.length > 0 && (
              <div className="image-previews">
                {imagePreviews.map((preview, index) => (
                  <div key={index} className="image-preview">
                    <img src={preview} alt={`Preview ${index + 1}`} />
                    <button
                      type="button"
                      onClick={() => removeImage(index)}
                      className="remove-image-btn"
                    >
                      <X size={16} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Form Actions */}
          <div className="form-actions">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Submitting...' : (editMode ? 'Update Request' : 'Submit Request')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default MaintenanceRequestForm;
