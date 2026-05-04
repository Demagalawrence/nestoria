import React, { useState, useEffect } from 'react';
import { 
  X, User, Phone, Calendar, MapPin, MessageSquare, 
  Star, Clock, CheckCircle, AlertCircle
} from 'lucide-react';
import agentService from '../services/agentService';
import './AgentRequestForm.css';

const AgentRequestForm = ({ 
  property, 
  onClose, 
  onSuccess, 
  requestType = 'property_consultation' 
}) => {
  const [formData, setFormData] = useState({
    request_type: requestType,
    title: '',
    description: '',
    property: property?.id || null,
    preferred_date: '',
    preferred_time: '',
    contact_method: 'phone',
    contact_details: '',
    priority: 'medium'
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [suggestedAgents, setSuggestedAgents] = useState([]);

  useEffect(() => {
    if (property) {
      setFormData(prev => ({
        ...prev,
        title: `Assistance with ${property.name}`,
        property: property.id
      }));
      
      // Get suggested agents for this property
      fetchSuggestedAgents();
    }
  }, [property]);

  const fetchSuggestedAgents = async () => {
    try {
      const params = {
        area: property?.district,
        specialization: property?.property_type === 'hostel' ? 'student_housing' : 'residential'
      };
      const response = await agentService.getAgents(params);
      setSuggestedAgents(response.data.slice(0, 3)); // Top 3 agents
    } catch (error) {
      console.error('Error fetching agents:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await agentService.createRequest(formData);
      
      if (response.data.assigned_agent) {
        // Agent was automatically assigned
        onSuccess(response.data);
        onClose();
      } else {
        // No agent available - show message
        setError('No agents are currently available. We will notify you when one becomes available.');
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to submit request');
    } finally {
      setLoading(false);
    }
  };

  const getRequestTypeInfo = (type) => {
    const types = {
      property_viewing: {
        icon: <MapPin size={16} />,
        title: 'Property Viewing',
        description: 'Schedule a visit to the property',
        color: '#3b82f6'
      },
      property_consultation: {
        icon: <MessageSquare size={16} />,
        title: 'Property Consultation',
        description: 'Get expert advice about this property',
        color: '#8b5cf6'
      },
      booking_assistance: {
        icon: <Calendar size={16} />,
        title: 'Reservation Assistance',
        description: 'Help with reservation process',
        color: '#10b981'
      },
      negotiation: {
        icon: <User size={16} />,
        title: 'Price Negotiation',
        description: 'Negotiate better terms',
        color: '#f59e0b'
      },
      document_help: {
        icon: <CheckCircle size={16} />,
        title: 'Document Assistance',
        description: 'Help with paperwork',
        color: '#06b6d4'
      },
      general_inquiry: {
        icon: <AlertCircle size={16} />,
        title: 'General Inquiry',
        description: 'General assistance needed',
        color: '#6b7280'
      }
    };
    return types[type] || types.general_inquiry;
  };

  const contactMethods = [
    { value: 'phone', label: 'Phone Call', icon: <Phone size={16} /> },
    { value: 'whatsapp', label: 'WhatsApp', icon: <MessageSquare size={16} /> },
    { value: 'email', label: 'Email', icon: <MessageSquare size={16} /> },
    { value: 'video_call', label: 'Video Call', icon: <User size={16} /> },
    { value: 'in_person', label: 'In Person', icon: <MapPin size={16} /> }
  ];

  return (
    <div className="agent-request-form-overlay">
      <div className="agent-request-form">
        <div className="form-header">
          <div className="header-content">
            <h2>Connect with an Agent</h2>
            <p>Get personalized assistance from our verified agents</p>
          </div>
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

          {/* Suggested Agents */}
          {suggestedAgents.length > 0 && (
            <div className="suggested-agents">
              <h3>Available Agents</h3>
              <div className="agents-list">
                {suggestedAgents.map(agent => (
                  <div key={agent.id} className="agent-card">
                    <div className="agent-info">
                      <div className="agent-avatar">
                        {agent.user_details?.profile_picture ? (
                          <img src={agent.user_details.profile_picture} alt={agent.user_details.full_name} />
                        ) : (
                          <User size={24} />
                        )}
                      </div>
                      <div className="agent-details">
                        <h4>{agent.user_details?.full_name}</h4>
                        <div className="agent-meta">
                          <div className="rating">
                            <Star size={14} fill="#f59e0b" color="#f59e0b" />
                            <span>{agent.average_rating || 'No rating'}</span>
                          </div>
                          <div className="response-time">
                            <Clock size={14} />
                            <span>{agent.response_time}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="agent-badges">
                      {agent.is_online && <span className="online-badge">Online</span>}
                      {agent.is_verified && <span className="verified-badge">Verified</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Request Type */}
          <div className="form-section">
            <h3>What do you need help with?</h3>
            <div className="request-types">
              {Object.entries({
                property_viewing: 'Schedule Property Visit',
                property_consultation: 'Property Information',
                booking_assistance: 'Reservation Help',
                negotiation: 'Price Negotiation',
                document_help: 'Document Assistance',
                general_inquiry: 'General Questions'
              }).map(([type, label]) => {
                const info = getRequestTypeInfo(type);
                return (
                  <label key={type} className="request-type-option">
                    <input
                      type="radio"
                      name="request_type"
                      value={type}
                      checked={formData.request_type === type}
                      onChange={handleChange}
                    />
                    <div className="option-content">
                      <div className="option-icon" style={{ color: info.color }}>
                        {info.icon}
                      </div>
                      <div className="option-text">
                        <h4>{label}</h4>
                        <p>{info.description}</p>
                      </div>
                    </div>
                  </label>
                );
              })}
            </div>
          </div>

          {/* Request Details */}
          <div className="form-section">
            <h3>Request Details</h3>
            
            <div className="form-group">
              <label>Title *</label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="Brief description of what you need"
                required
              />
            </div>

            <div className="form-group">
              <label>Description *</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Provide more details about your request..."
                rows={4}
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Priority</label>
                <select name="priority" value={formData.priority} onChange={handleChange}>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
            </div>
          </div>

          {/* Scheduling */}
          <div className="form-section">
            <h3>Preferred Schedule</h3>
            
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
                <label>Contact Method</label>
                <select name="contact_method" value={formData.contact_method} onChange={handleChange}>
                  {contactMethods.map(method => (
                    <option key={method.value} value={method.value}>
                      {method.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Additional Contact Details</label>
              <textarea
                name="contact_details"
                value={formData.contact_details}
                onChange={handleChange}
                placeholder="Any additional information for contacting you..."
                rows={2}
              />
            </div>
          </div>

          {/* Submit */}
          <div className="form-actions">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Submitting...' : 'Connect with Agent'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AgentRequestForm;
