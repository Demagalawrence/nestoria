import React, { useState, useEffect } from 'react';
import { 
  Wrench, AlertCircle, Clock, CheckCircle, User, Calendar, 
  Filter, Search, Plus, Bell, TrendingUp, MessageSquare,
  Camera, Paperclip, MoreVertical
} from 'lucide-react';
import maintenanceService from '../services/maintenanceService';
import './MaintenanceDashboard.css';

const MaintenanceDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [requests, setRequests] = useState([]);
  const [stats, setStats] = useState(null);
  const [, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterPriority, setFilterPriority] = useState('');
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [notifications] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [requestsRes, statsRes, categoriesRes] = await Promise.all([
        maintenanceService.getRequests(),
        maintenanceService.getStats(),
        maintenanceService.getCategories()
      ]);
      
      setRequests(requestsRes.data);
      setStats(statsRes.data);
      setCategories(categoriesRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: '#f59e0b',
      acknowledged: '#3b82f6',
      in_progress: '#8b5cf6',
      completed: '#10b981',
      cancelled: '#ef4444',
      on_hold: '#6b7280'
    };
    return colors[status] || '#6b7280';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      urgent: '#ef4444',
      high: '#f59e0b',
      medium: '#3b82f6',
      low: '#10b981'
    };
    return colors[priority] || '#6b7280';
  };

  const filteredRequests = requests.filter(request => {
    const matchesSearch = request.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         request.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         request.reference_number.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = !filterStatus || request.status === filterStatus;
    const matchesPriority = !filterPriority || request.priority === filterPriority;
    
    return matchesSearch && matchesStatus && matchesPriority;
  });

  const StatCard = ({ icon, title, value, color, trend }) => (
    <div className="stat-card">
      <div className="stat-icon" style={{ backgroundColor: color + '20', color }}>
        {icon}
      </div>
      <div className="stat-content">
        <h3>{title}</h3>
        <p className="stat-value">{value}</p>
        {trend && (
          <div className="stat-trend">
            <TrendingUp size={14} />
            <span>{trend}</span>
          </div>
        )}
      </div>
    </div>
  );

  const RequestCard = ({ request }) => (
    <div 
      className="request-card"
      onClick={() => setSelectedRequest(request)}
    >
      <div className="request-header">
        <div className="request-info">
          <h4>{request.title}</h4>
          <span className="reference-number">{request.reference_number}</span>
        </div>
        <div className="request-actions">
          <button className="action-btn">
            <MoreVertical size={16} />
          </button>
        </div>
      </div>
      
      <div className="request-body">
        <p className="request-description">{request.description.substring(0, 150)}...</p>
        
        <div className="request-meta">
          <div className="meta-item">
            <div 
              className="status-badge"
              style={{ backgroundColor: getStatusColor(request.status) }}
            >
              {request.status.replace('_', ' ')}
            </div>
          </div>
          <div className="meta-item">
            <div 
              className="priority-badge"
              style={{ backgroundColor: getPriorityColor(request.priority) }}
            >
              {request.priority}
            </div>
          </div>
        </div>
        
        <div className="request-footer">
          <div className="request-property">
            <Calendar size={14} />
            <span>{request.property_details?.name}</span>
          </div>
          <div className="request-date">
            <Clock size={14} />
            <span>{new Date(request.created_at).toLocaleDateString()}</span>
          </div>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="maintenance-dashboard">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading maintenance dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="maintenance-dashboard">
      <div className="dashboard-header">
        <div className="header-content">
          <h1>Maintenance Management</h1>
          <p>Manage and track all maintenance requests</p>
        </div>
        <div className="header-actions">
          <button className="btn-primary" onClick={() => setActiveTab('requests')}>
            <Plus size={16} />
            New Request
          </button>
          <button className="btn-secondary">
            <Bell size={16} />
            Notifications
            {notifications.length > 0 && (
              <span className="notification-badge">{notifications.length}</span>
            )}
          </button>
        </div>
      </div>

      <div className="dashboard-tabs">
        <button 
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab-btn ${activeTab === 'requests' ? 'active' : ''}`}
          onClick={() => setActiveTab('requests')}
        >
          Requests
        </button>
        <button 
          className={`tab-btn ${activeTab === 'calendar' ? 'active' : ''}`}
          onClick={() => setActiveTab('calendar')}
        >
          Calendar
        </button>
        <button 
          className={`tab-btn ${activeTab === 'reports' ? 'active' : ''}`}
          onClick={() => setActiveTab('reports')}
        >
          Reports
        </button>
      </div>

      {activeTab === 'overview' && (
        <div className="overview-content">
          <div className="stats-grid">
            <StatCard
              icon={<AlertCircle size={24} />}
              title="Pending Requests"
              value={stats?.pending_requests || 0}
              color="#f59e0b"
            />
            <StatCard
              icon={<Clock size={24} />}
              title="In Progress"
              value={stats?.in_progress_requests || 0}
              color="#3b82f6"
            />
            <StatCard
              icon={<CheckCircle size={24} />}
              title="Completed"
              value={stats?.completed_requests || 0}
              color="#10b981"
            />
            <StatCard
              icon={<AlertCircle size={24} />}
              title="Urgent"
              value={stats?.urgent_requests || 0}
              color="#ef4444"
            />
          </div>

          <div className="dashboard-grid">
            <div className="recent-requests">
              <h3>Recent Requests</h3>
              <div className="requests-list">
                {stats?.recent_requests?.map(request => (
                  <RequestCard key={request.id} request={request} />
                ))}
              </div>
            </div>

            <div className="quick-actions">
              <h3>Quick Actions</h3>
              <div className="actions-grid">
                <button className="action-card">
                  <Plus size={20} />
                  <span>Create Request</span>
                </button>
                <button className="action-card">
                  <Calendar size={20} />
                  <span>View Schedule</span>
                </button>
                <button className="action-card">
                  <MessageSquare size={20} />
                  <span>Messages</span>
                </button>
                <button className="action-card">
                  <Camera size={20} />
                  <span>Upload Photos</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'requests' && (
        <div className="requests-content">
          <div className="requests-header">
            <div className="search-filters">
              <div className="search-bar">
                <Search size={16} />
                <input
                  type="text"
                  placeholder="Search requests..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              
              <div className="filters">
                <select 
                  value={filterStatus} 
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <option value="">All Status</option>
                  <option value="pending">Pending</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                </select>
                
                <select 
                  value={filterPriority} 
                  onChange={(e) => setFilterPriority(e.target.value)}
                >
                  <option value="">All Priority</option>
                  <option value="urgent">Urgent</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
            </div>
          </div>

          <div className="requests-grid">
            {filteredRequests.map(request => (
              <RequestCard key={request.id} request={request} />
            ))}
          </div>
        </div>
      )}

      {selectedRequest && (
        <div className="request-detail-modal">
          <div className="modal-overlay" onClick={() => setSelectedRequest(null)} />
          <div className="modal-content">
            <div className="modal-header">
              <h2>{selectedRequest.title}</h2>
              <button onClick={() => setSelectedRequest(null)}>×</button>
            </div>
            <div className="modal-body">
              {/* Request details will be implemented here */}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MaintenanceDashboard;
