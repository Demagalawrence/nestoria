import React, { useState, useEffect } from 'react';
import { 
  Home, Users, Building, Calendar, CreditCard, Bell, Settings, 
  Plus, Edit, Trash2, Search, Filter, LogOut, Shield, CheckCircle, X,
  TrendingUp, DollarSign, MapPin, Phone, Mail, Star, Eye, Save
} from 'lucide-react';
import api from '../api/axios';
import './AdminDashboard.css';

const initialPropertyFormData = {
  name: '',
  description: '',
  property_type: 'hostel',
  target_audience: 'university_students',
  rent_per_month: '',
  district: 'Kampala',
  address_line_1: '',
  total_rooms: '',
  available_rooms: '',
  amenities: '',
  rules: '',
  contact_person: '',
  contact_number: '',
  owner_id: '',
  is_approved: true
};

const initialOwnerFormData = {
  email: '',
  first_name: '',
  last_name: '',
  password: 'tempPassword123',
  confirm_password: 'tempPassword123',
  role: 'owner',
  contact_number: '',
  alternate_number: '',
  date_of_birth: '',
  gender: '',
  occupation: '',
  company_name: '',
  annual_income: '',
  permanent_address: '',
  current_address: '',
  emergency_contact_name: '',
  emergency_contact_number: '',
  emergency_contact_relation: ''
};

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [properties, setProperties] = useState([]);
  const [users, setUsers] = useState([]);
  const [reservations, setReservations] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [authChecking, setAuthChecking] = useState(true);
  const [, setUser] = useState(null);
  const [showAddPropertyModal, setShowAddPropertyModal] = useState(false);
  const [showUserModal, setShowUserModal] = useState(false);
  const [showOwnerModal, setShowOwnerModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [ownerProfilePicture, setOwnerProfilePicture] = useState(null);
  const [ownerNationalIdCard, setOwnerNationalIdCard] = useState(null);
  const [ownerProfilePreview, setOwnerProfilePreview] = useState(null);
  const [ownerIdPreview, setOwnerIdPreview] = useState(null);
  const [propertyImages, setPropertyImages] = useState([]);
  const [propertyImagePreviews, setPropertyImagePreviews] = useState([]);
  const [propertyFormData, setPropertyFormData] = useState(initialPropertyFormData);
  
  const [userFormData, setUserFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    role: 'tenant',
    contact_number: '',
    alternate_number: '',
    date_of_birth: '',
    gender: '',
    occupation: '',
    company_name: '',
    annual_income: '',
    permanent_address: '',
    current_address: '',
    emergency_contact_name: '',
    emergency_contact_number: '',
    emergency_contact_relation: ''
  });
  
  const [ownerFormData, setOwnerFormData] = useState(initialOwnerFormData);

  const ownerOptions = users.filter(user => ['owner', 'agent', 'admin'].includes(user.role));
  const getOwnerDisplayName = (owner) => {
    if (!owner) return 'Unassigned';
    const fullName = `${owner.first_name || ''} ${owner.last_name || ''}`.trim();
    return fullName || owner.name || owner.username || owner.email || 'Unassigned';
  };
  
  const handleLogout = () => {
    // Clear all admin-related data
    setUser(null);
    setActiveTab('dashboard');
    setProperties([]);
    setUsers([]);
    setReservations([]);
    setSearchTerm('');
    setLoading(true);
    
    // Clear all storage
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    
    // Force redirect to login page
    window.location.href = '/login'; // Force full page reload and redirect
  };

  useEffect(() => {
    checkAdminAccess();
  }, []);

  const checkAdminAccess = async () => {
    try {
      // Add timeout to prevent hanging
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Admin access check timeout')), 10000)
      );
      
      // First check if we have stored authentication
      const storedUser = localStorage.getItem('user') || sessionStorage.getItem('user');
      const token = localStorage.getItem('token');
      
      console.log('AdminDashboard Auth Check:');
      console.log('Stored user:', storedUser);
      console.log('Token:', token);
      
      if (!storedUser || !token) {
        console.log('No stored authentication, redirecting to home...');
        // Show error message before redirect
        alert('Please login as an administrator to access the admin panel');
        window.location.href = '/login';
        return;
      }
      
      // Parse stored user to check role before API call
      let parsedUser;
      try {
        parsedUser = JSON.parse(storedUser);
      } catch {
        console.log('Invalid stored user data, clearing and redirecting...');
        localStorage.removeItem('user');
        sessionStorage.removeItem('user');
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        alert('Invalid session. Please login again.');
        window.location.href = '/login';
        return;
      }
      
      // Quick role check before API call
      if (parsedUser.role !== 'admin') {
        console.log('Stored user is not admin, redirecting...');
        alert('Access denied. Administrator privileges required.');
        window.location.href = '/';
        return;
      }
      
      // If we have stored data, try to verify with API (with timeout)
      const userRes = await Promise.race([
        api.get('/accounts/profile/'),
        timeoutPromise
      ]);
      
      const userData = userRes.data;
      
      console.log('API User Data:', userData);
      
      // Check if user is admin
      if (userData.role !== 'admin') {
        console.log('API user is not admin, redirecting to home...');
        alert('Access denied. Administrator privileges required.');
        window.location.href = '/';
        return;
      }
      
      // Set user and load data
      setUser(userData);
      
      // Load data with error handling to prevent hanging
      try {
        await fetchAdminData();
      } catch (error) {
        console.warn('Failed to fetch admin data:', error);
      }
      
      setLoading(false);
      setAuthChecking(false);
      
      console.log('Admin access granted, dashboard loaded');
      
    } catch (error) {
      console.error('Admin access check failed:', error);
      
      // Handle timeout specifically
      if (error.message === 'Admin access check timeout') {
        console.log('Admin access check timed out, proceeding with stored data...');
        // Proceed with stored user data if API times out
        const storedUser = localStorage.getItem('user') || sessionStorage.getItem('user');
        if (storedUser) {
          try {
            const parsedUser = JSON.parse(storedUser);
            if (parsedUser.role === 'admin') {
              setUser(parsedUser);
              setLoading(false);
              setAuthChecking(false);
              console.log('Admin access granted via stored data (timeout fallback)');
              return;
            }
          } catch (e) {
            console.error('Failed to parse stored user:', e);
          }
        }
      }
      
      // More specific error handling
      if (error.response?.status === 401) {
        alert('Session expired. Please login again.');
        window.location.href = '/login';
      } else if (error.response?.status === 403) {
        alert('Access denied. Administrator privileges required.');
        window.location.href = '/';
      } else {
        alert('Unable to verify admin access. Please try again.');
        window.location.href = '/';
      }
      
      // Clear invalid stored data and redirect
      localStorage.removeItem('user');
      sessionStorage.removeItem('user');
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
    }
  };

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      const [propertiesRes, usersRes, reservationsRes] = await Promise.all([
        api.get('/properties/'),
        api.get('/accounts/users/'),
        api.get('/bookings/')
      ]);
      setProperties(propertiesRes.data?.results || []);
      setUsers(usersRes.data?.results || []);
      setReservations(reservationsRes.data?.results || []);
    } catch (error) {
      console.error('Error fetching admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProperty = async (id) => {
    if (window.confirm('Delete this property?')) {
      try {
        await api.delete(`/properties/${id}/delete/`);
        setProperties(properties.filter(p => p.id !== id));
      } catch (error) {
        console.error('Error deleting property:', error);
      }
    }
  };

  const handleDeleteUser = async (id) => {
    if (window.confirm('Delete this user?')) {
      try {
        await api.delete(`/accounts/users/${id}/`);
        setUsers(users.filter(u => u.id !== id));
      } catch (error) {
        console.error('Error deleting user:', error);
      }
    }
  };

  const handleApproveProperty = async (id) => {
    try {
      const property = properties.find(p => p.id === id);
      const nextApprovalState = !property?.is_approved;
      await api.patch(`/properties/${id}/update/`, { is_approved: nextApprovalState });
      setProperties(properties.map(p => p.id === id ? { ...p, is_approved: nextApprovalState } : p));
    } catch (error) {
      console.error('Error approving property:', error);
    }
  };

  const handleAddProperty = async () => {
    try {
      if (!propertyFormData.name || !propertyFormData.description || !propertyFormData.address_line_1 || !propertyFormData.rent_per_month || !propertyFormData.total_rooms) {
        alert('Please fill in all required fields: property name, description, address, rent, and number of rooms.');
        return;
      }

      const totalRooms = parseInt(propertyFormData.total_rooms, 10);
      const availableRooms = propertyFormData.available_rooms ? parseInt(propertyFormData.available_rooms, 10) : totalRooms;

      if (Number.isNaN(totalRooms) || totalRooms < 1 || Number.isNaN(availableRooms) || availableRooms < 0) {
        alert('Please enter a valid room count.');
        return;
      }

      if (availableRooms > totalRooms) {
        alert('Available rooms cannot be more than total rooms.');
        return;
      }

      const rentPerMonth = parseFloat(propertyFormData.rent_per_month);
      if (Number.isNaN(rentPerMonth) || rentPerMonth <= 0) {
        alert('Please enter a valid rent amount.');
        return;
      }

      const submitData = new FormData();

      const propertyPayload = {
        ...propertyFormData,
        total_rooms: totalRooms,
        available_rooms: Math.min(availableRooms, totalRooms),
        rent_per_month: rentPerMonth,
        country: 'Uganda',
        gender_preference: 'any',
        is_active: true,
        amenities: propertyFormData.amenities 
          ? propertyFormData.amenities.split(',').map(item => item.trim()).filter(item => item.length > 0)
          : []
      };

      Object.entries(propertyPayload).forEach(([key, value]) => {
        if (value !== '' && value !== null && value !== undefined) {
          // Handle JSON arrays properly
          if ((key === 'amenities' || key === 'safety_features') && Array.isArray(value)) {
            submitData.append(key, JSON.stringify(value));
          } else {
            submitData.append(key, value);
          }
        }
      });
      
      propertyImages.forEach((image) => {
        submitData.append('property_images', image);
      });

      const config = {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      };

      await api.post('/properties/create/', submitData, config);
      await fetchAdminData();
      
      setShowAddPropertyModal(false);
      setPropertyFormData(initialPropertyFormData);
      setPropertyImages([]);
      setPropertyImagePreviews([]);
      
      alert('Property created successfully!');
    } catch (error) {
      console.error('Error creating property:', error);
      console.error('Error response data:', error.response?.data);
      console.error('Error status:', error.response?.status);
      
      if (error.response?.data) {
        const errorData = error.response.data;
        if (typeof errorData === 'object') {
          const errorMessages = Object.entries(errorData)
            .map(([field, messages]) => {
              const friendlyField = field.charAt(0).toUpperCase() + field.slice(1);
              return `${friendlyField}: ${Array.isArray(messages) ? messages.join(', ') : messages}`;
            })
            .join('; ');
          alert(`Property creation failed: ${errorMessages}`);
        } else {
          alert(`Property creation failed: ${errorData.detail || errorData.error || 'Unknown error'}`);
        }
      } else {
        alert('Error creating property. Please check the console for details.');
      }
    }
  };

  const handlePropertyFormChange = (e) => {
    const { name, value } = e.target;
    setPropertyFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePropertyImagesChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      // Validate files
      const validFiles = files.filter(file => {
        if (file.size > 10 * 1024 * 1024) { // 10MB limit per image
          alert(`Image ${file.name} must be less than 10MB`);
          return false;
        }
        if (!file.type.startsWith('image/')) {
          alert(`File ${file.name} must be an image file`);
          return false;
        }
        return true;
      });

      if (validFiles.length > 0) {
        setPropertyImages(prev => [...prev, ...validFiles]);
        
        // Create previews for new images
        const newPreviews = validFiles.map(file => URL.createObjectURL(file));
        setPropertyImagePreviews(prev => [...prev, ...newPreviews]);
      }
    }
  };

  const removePropertyImage = (index) => {
    setPropertyImages(prev => prev.filter((_, i) => i !== index));
    setPropertyImagePreviews(prev => prev.filter((_, i) => i !== index));
  };

  const handleUserFormChange = (e) => {
    const { name, value } = e.target;
    setUserFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAddUser = () => {
    setEditingUser(null);
    setUserFormData({
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      role: 'tenant',
      contact_number: '',
      alternate_number: '',
      date_of_birth: '',
      gender: '',
      occupation: '',
      company_name: '',
      annual_income: '',
      permanent_address: '',
      current_address: '',
      emergency_contact_name: '',
      emergency_contact_number: '',
      emergency_contact_relation: ''
    });
    setShowUserModal(true);
  };

  const handleEditUser = (user) => {
    setEditingUser(user);
    setUserFormData({
      username: user.username || '',
      email: user.email || '',
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      role: user.role || 'tenant',
      contact_number: user.contact_number || '',
      alternate_number: user.alternate_number || '',
      date_of_birth: user.date_of_birth || '',
      gender: user.gender || '',
      occupation: user.occupation || '',
      company_name: user.company_name || '',
      annual_income: user.annual_income || '',
      permanent_address: user.permanent_address || '',
      current_address: user.current_address || '',
      emergency_contact_name: user.emergency_contact_name || '',
      emergency_contact_number: user.emergency_contact_number || '',
      emergency_contact_relation: user.emergency_contact_relation || ''
    });
    setShowUserModal(true);
  };

  const handleSaveUser = async () => {
    try {
      if (editingUser) {
        // Update existing user
        await api.patch(`/accounts/users/${editingUser.id}/`, userFormData);
        setUsers(users.map(u => u.id === editingUser.id ? { ...u, ...userFormData } : u));
      } else {
        // Create new user
        const userData = {
          ...userFormData,
          password: 'tempPassword123',
          confirm_password: 'tempPassword123'
        };
        const response = await api.post('/accounts/register/', userData);
        setUsers([...users, response.data.user || response.data]);
      }
      
      setShowUserModal(false);
      alert(`User ${editingUser ? 'updated' : 'created'} successfully!`);
    } catch (error) {
      console.error('Error saving user:', error);
      alert('Error saving user. Please check the console for details.');
    }
  };

  const handleOwnerFormChange = (e) => {
    const { name, value } = e.target;
    setOwnerFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAddOwner = () => {
    setOwnerFormData(initialOwnerFormData);
    setOwnerProfilePicture(null);
    setOwnerNationalIdCard(null);
    setOwnerProfilePreview(null);
    setOwnerIdPreview(null);
    setShowOwnerModal(true);
  };

  const handleOwnerProfilePictureChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        alert('Profile picture must be less than 5MB');
        return;
      }
      if (!file.type.startsWith('image/')) {
        alert('Profile picture must be an image file');
        return;
      }
      setOwnerProfilePicture(file);
      setOwnerProfilePreview(URL.createObjectURL(file));
    }
  };

  const handleOwnerNationalIdChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        alert('National ID card must be less than 10MB');
        return;
      }
      if (!file.type.startsWith('image/')) {
        alert('National ID card must be an image file');
        return;
      }
      setOwnerNationalIdCard(file);
      setOwnerIdPreview(URL.createObjectURL(file));
    }
  };

  const handleSaveOwner = async () => {
    try {
      // Validate required files
      if (!ownerProfilePicture) {
        alert('Please upload a profile picture');
        return;
      }
      
      if (!ownerNationalIdCard) {
        alert('Please upload a national ID card for verification');
        return;
      }

      // Create FormData for file upload
      const submitData = new FormData();
      
      // Add all form fields
      Object.keys(ownerFormData).forEach(key => {
        if (ownerFormData[key]) {
          submitData.append(key, ownerFormData[key]);
        }
      });
      submitData.append('id_proof_type', 'other');
      
      // Add files
      submitData.append('profile_picture', ownerProfilePicture);
      submitData.append('national_id_card', ownerNationalIdCard);

      // Set proper headers for FormData
      const config = {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      };

      const response = await api.post('/accounts/register/', submitData, config);
      setUsers([...users, response.data.user || response.data]);
      
      setShowOwnerModal(false);
      alert('Property owner registered successfully with documents!');
    } catch (error) {
      console.error('Error registering owner:', error);
      alert('Error registering owner. Please check the console for details.');
    }
  };

  const renderDashboard = () => (
    <div className="admin-stats-grid">
      <div className="stat-card">
        <div className="stat-icon blue"><Building size={24} /></div>
        <div className="stat-content">
          <h3>{properties.length}</h3>
          <p>Total Properties</p>
        </div>
      </div>
      <div className="stat-card">
        <div className="stat-icon green"><Users size={24} /></div>
        <div className="stat-content">
          <h3>{users.length}</h3>
          <p>Total Users</p>
        </div>
      </div>
      <div className="stat-card">
        <div className="stat-icon orange"><Calendar size={24} /></div>
        <div className="stat-content">
          <h3>{reservations.length}</h3>
          <p>Total Reservations</p>
        </div>
      </div>
      <div className="stat-card">
        <div className="stat-icon purple"><TrendingUp size={24} /></div>
        <div className="stat-content">
          <h3>UGX 2.5M</h3>
          <p>Total Revenue</p>
        </div>
      </div>
    </div>
  );

  const renderProperties = () => (
    <div className="admin-table-container">
      <div className="table-header">
        <h3>Properties</h3>
        <div className="table-actions">
          <div className="search-box">
            <Search size={16} />
            <input
              type="text"
              placeholder="Search properties..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <button className="btn-primary" onClick={() => setShowAddPropertyModal(true)}>
            <Plus size={16} />
            Add Property
          </button>
        </div>
      </div>
      
      <div className="admin-table">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Audience</th>
              <th>Owner</th>
              <th>Price</th>
              <th>Location</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {properties.filter(p => 
              p.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
              p.owner?.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
              p.owner_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
              p.target_audience?.toLowerCase().includes(searchTerm.toLowerCase())
            ).map(property => (
              <tr key={property.id}>
                <td>{property.name}</td>
                <td>{property.property_type}</td>
                <td>{property.target_audience === 'university_students' ? 'University' : property.target_audience}</td>
                <td>{property.owner?.username || property.owner_username || property.owner_name}</td>
                <td>UGX {property.rent_per_month}</td>
                <td>{property.district}</td>
                <td>
                  <span className={`status-badge ${property.is_approved ? 'approved' : 'pending'}`}>
                    {property.is_approved ? 'Approved' : 'Pending'}
                  </span>
                </td>
                <td>
                  <div className="action-buttons">
                    <button className="btn-view"><Eye size={14} /></button>
                    <button className="btn-edit"><Edit size={14} /></button>
                    {property.is_approved ? (
                      <button className="btn-warning" onClick={() => handleApproveProperty(property.id)}>
                        <X size={14} />
                      </button>
                    ) : (
                      <button className="btn-success" onClick={() => handleApproveProperty(property.id)}>
                        <CheckCircle size={14} />
                      </button>
                    )}
                    <button className="btn-danger" onClick={() => handleDeleteProperty(property.id)}>
                      <Trash2 size={14} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderUsers = () => (
    <div className="admin-table-container">
      <div className="table-header">
        <h3>Users</h3>
        <div className="table-actions">
          <div className="search-box">
            <Search size={16} />
            <input
              type="text"
              placeholder="Search users..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <button className="btn-primary" onClick={handleAddUser}>
            <Plus size={16} />
            Add User
          </button>
          <button className="btn-secondary" onClick={handleAddOwner} style={{ marginLeft: '10px' }}>
            <Plus size={16} />
            Add Property Owner
          </button>
        </div>
      </div>
      
      <div className="admin-table">
        <table>
          <thead>
            <tr>
              <th>Username</th>
              <th>Email</th>
              <th>Role</th>
              <th>Phone</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.filter(user => 
              user.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
              user.email?.toLowerCase().includes(searchTerm.toLowerCase())
            ).map(user => (
              <tr key={user.id}>
                <td>{user.username}</td>
                <td>{user.email}</td>
                <td>
                  <span className={`role-badge ${user.role}`}>
                    {user.role}
                  </span>
                </td>
                <td>{user.contact_number || 'N/A'}</td>
                <td>
                  <span className="status-badge active">
                    Active
                  </span>
                </td>
                <td>
                  <div className="action-buttons">
                    <button className="btn-view"><Eye size={14} /></button>
                    <button className="btn-edit" onClick={() => handleEditUser(user)}><Edit size={14} /></button>
                    <button className="btn-danger" onClick={() => handleDeleteUser(user.id)}>
                      <Trash2 size={14} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderReservations = () => (
    <div className="admin-table-container">
      <div className="table-header">
        <h3>Reservations</h3>
        <div className="table-actions">
          <div className="search-box">
            <Search size={16} />
            <input
              type="text"
              placeholder="Search reservations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
      </div>
      
      <div className="admin-table">
        <table>
          <thead>
            <tr>
              <th>Reference</th>
              <th>Property</th>
              <th>User</th>
              <th>Check-in</th>
              <th>Check-out</th>
              <th>Status</th>
              <th>Amount</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {reservations.filter(reservation => 
              reservation.property_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
              reservation.user_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
              reservation.booking_reference?.toLowerCase().includes(searchTerm.toLowerCase())
            ).map(reservation => (
              <tr key={reservation.id}>
                <td>{reservation.booking_reference || 'N/A'}</td>
                <td>{reservation.property_name || 'N/A'}</td>
                <td>{reservation.user_name || 'N/A'}</td>
                <td>{reservation.start_date || 'N/A'}</td>
                <td>{reservation.end_date || 'N/A'}</td>
                <td>
                  <span className={`status-badge ${reservation.status}`}>
                    {reservation.status}
                  </span>
                </td>
                <td>UGX {reservation.final_amount || '0'}</td>
                <td>
                  <div className="action-buttons">
                    <button className="btn-view"><Eye size={14} /></button>
                    <button className="btn-edit"><Edit size={14} /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  if (authChecking) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        flexDirection: 'column',
        backgroundColor: '#f8f9fa'
      }}>
        <div style={{ 
          width: '50px', 
          height: '50px', 
          border: '5px solid #e3e3e3', 
          borderTop: '5px solid #1a656e', 
          borderRadius: '50%', 
          animation: 'spin 1s linear infinite' 
        }}></div>
        <p style={{ marginTop: '20px', color: '#666' }}>Verifying admin access...</p>
        <style jsx>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  if (loading) {
    return <div className="admin-loading">Loading admin dashboard...</div>;
  }

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <div className="header-left">
          <h1>Admin Dashboard</h1>
          <p>Manage your hostel rental platform</p>
        </div>
        <div className="header-right">
          <div className="admin-badge">
            <Shield size={16} />
            <span>Administrator</span>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            <LogOut size={16} />
            Logout
          </button>
        </div>
      </div>

      <div className="admin-nav-bar">
        <button 
          className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <Home size={16} />
          Dashboard
        </button>
        <button 
          className={`nav-item ${activeTab === 'properties' ? 'active' : ''}`}
          onClick={() => setActiveTab('properties')}
        >
          <Building size={16} />
          Properties
        </button>
        <button 
          className={`nav-item ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          <Users size={16} />
          Users
        </button>
        <button 
          className={`nav-item ${activeTab === 'reservations' ? 'active' : ''}`}
          onClick={() => setActiveTab('reservations')}
        >
          <Calendar size={16} />
          Reservations
        </button>
      </div>

      <div className="admin-content">
        {activeTab === 'dashboard' && renderDashboard()}
        {activeTab === 'properties' && renderProperties()}
        {activeTab === 'users' && renderUsers()}
        {activeTab === 'reservations' && renderReservations()}
      </div>

      {/* Add Property Modal */}
      {showAddPropertyModal && (
        <div className="modal-overlay">
          <div className="modal" style={{ maxWidth: '800px', width: '95%', maxHeight: '90vh', overflowY: 'auto' }}>
            <div className="modal-header">
              <h3>Add New Property</h3>
              <button className="modal-close" onClick={() => setShowAddPropertyModal(false)}>
                <X size={20} />
              </button>
            </div>
            
            <div className="modal-body">
              {/* Property Images Upload */}
              <div className="form-group">
                <label>Property Images</label>
                <div className="file-upload-container">
                  <div className="property-images-preview">
                    {propertyImagePreviews.length > 0 ? (
                      <div className="images-grid">
                        {propertyImagePreviews.map((preview, index) => (
                          <div key={index} className="image-preview-item">
                            <img src={preview} alt={`Property ${index + 1}`} className="preview-image" />
                            <button 
                              type="button" 
                              className="remove-image-btn"
                              onClick={() => removePropertyImage(index)}
                            >
                              <X size={16} />
                            </button>
                          </div>
                        ))}
                        <div className="add-more-image">
                          <input
                            type="file"
                            accept="image/*"
                            multiple
                            onChange={handlePropertyImagesChange}
                            className="file-input"
                            style={{ display: 'none' }}
                            id="add-more-images"
                          />
                          <label htmlFor="add-more-images" className="add-image-label">
                            <Plus size={24} />
                            <span>Add More</span>
                          </label>
                        </div>
                      </div>
                    ) : (
                      <div className="preview-placeholder">
                        <span>🏠</span>
                        <p>No property images selected</p>
                        <input
                          type="file"
                          accept="image/*"
                          multiple
                          onChange={handlePropertyImagesChange}
                          className="file-input"
                          style={{ display: 'none' }}
                          id="property-images"
                        />
                        <label htmlFor="property-images" className="file-upload-btn">
                          Choose Property Images
                        </label>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <h4 style={{ marginBottom: '15px', color: '#1a656e' }}>Ownership</h4>
              <div className="form-group" style={{ marginBottom: '25px' }}>
                <label>Property Owner</label>
                <select
                  name="owner_id"
                  value={propertyFormData.owner_id}
                  onChange={handlePropertyFormChange}
                >
                  <option value="">Use my admin account</option>
                  {ownerOptions.map(owner => (
                    <option key={owner.id} value={owner.id}>
                      {getOwnerDisplayName(owner)} ({owner.email || owner.username})
                    </option>
                  ))}
                </select>
              </div>

              <h4 style={{ marginBottom: '15px', color: '#1a656e' }}>Property Details</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginBottom: '25px' }}>
                <div className="form-group">
                  <label>Property Name *</label>
                  <input
                    type="text"
                    name="name"
                    value={propertyFormData.name}
                    onChange={handlePropertyFormChange}
                  />
                </div>
                <div className="form-group">
                  <label>Property Type</label>
                  <select
                    name="property_type"
                    value={propertyFormData.property_type}
                    onChange={handlePropertyFormChange}
                  >
                    <option value="hostel">Hostel</option>
                    <option value="apartment">Apartment</option>
                    <option value="house">House</option>
                    <option value="studio">Studio</option>
                    <option value="single_room">Single Room</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Audience</label>
                  <select
                    name="target_audience"
                    value={propertyFormData.target_audience}
                    onChange={handlePropertyFormChange}
                  >
                    <option value="university_students">University Students</option>
                    <option value="public">Public</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Rent per Month (UGX)</label>
                  <input
                    type="number"
                    name="rent_per_month"
                    value={propertyFormData.rent_per_month}
                    onChange={handlePropertyFormChange}
                    placeholder="0"
                  />
                </div>
                <div className="form-group">
                  <label>Total Rooms</label>
                  <input
                    type="number"
                    name="total_rooms"
                    value={propertyFormData.total_rooms}
                    onChange={handlePropertyFormChange}
                    placeholder="0"
                  />
                </div>
                <div className="form-group">
                  <label>Available Rooms</label>
                  <input
                    type="number"
                    name="available_rooms"
                    value={propertyFormData.available_rooms}
                    onChange={handlePropertyFormChange}
                    placeholder="Defaults to total rooms"
                  />
                </div>
                <div className="form-group">
                  <label>District</label>
                  <input
                    type="text"
                    name="district"
                    value={propertyFormData.district}
                    onChange={handlePropertyFormChange}
                    placeholder="e.g., Kampala"
                  />
                </div>
              </div>

              <div className="form-group" style={{ marginBottom: '25px' }}>
                <label>Address</label>
                <input
                  type="text"
                  name="address_line_1"
                  value={propertyFormData.address_line_1}
                  onChange={handlePropertyFormChange}
                  placeholder="Full property address"
                />
              </div>

              <div className="form-group" style={{ marginBottom: '25px' }}>
                <label>Description</label>
                <textarea
                  name="description"
                  value={propertyFormData.description}
                  onChange={handlePropertyFormChange}
                  placeholder="Describe the property..."
                  rows="3"
                />
              </div>

              <div className="form-group" style={{ marginBottom: '25px' }}>
                <label>Amenities (comma separated)</label>
                <textarea
                  name="amenities"
                  value={propertyFormData.amenities}
                  onChange={handlePropertyFormChange}
                  placeholder="e.g., WiFi, Parking, Security, Water, Electricity"
                  rows="2"
                />
              </div>

              <div className="form-group" style={{ marginBottom: '25px' }}>
                <label>House Rules</label>
                <textarea
                  name="rules"
                  value={propertyFormData.rules}
                  onChange={handlePropertyFormChange}
                  placeholder="e.g., No pets, No smoking, Quiet hours"
                  rows="2"
                />
              </div>

              <h4 style={{ marginBottom: '15px', color: '#1a656e' }}>Contact Information</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginBottom: '25px' }}>
                <div className="form-group">
                  <label>Contact Person</label>
                  <input
                    type="text"
                    name="contact_person"
                    value={propertyFormData.contact_person}
                    onChange={handlePropertyFormChange}
                    placeholder="Property manager name"
                  />
                </div>
                <div className="form-group">
                  <label>Contact Phone</label>
                  <input
                    type="tel"
                    name="contact_number"
                    value={propertyFormData.contact_number}
                    onChange={handlePropertyFormChange}
                    placeholder="+256..."
                  />
                </div>
              </div>

              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    name="is_approved"
                    checked={propertyFormData.is_approved}
                    onChange={(e) => setPropertyFormData(prev => ({
                      ...prev,
                      is_approved: e.target.checked
                    }))}
                  />
                  {' '}Approve this property immediately
                </label>
              </div>
            </div>
            
            <div className="form-actions">
              <button className="btn-secondary" onClick={() => setShowAddPropertyModal(false)}>
                Cancel
              </button>
              <button className="btn-primary" onClick={handleAddProperty}>
                <Save size={16} />
                Create Property
              </button>
            </div>
          </div>
        </div>
      )}

      {/* User Management Modal */}
      {showUserModal && (
        <div className="modal-overlay">
          <div className="modal" style={{ maxWidth: '900px', width: '95%', maxHeight: '90vh', overflowY: 'auto' }}>
            <div className="modal-header">
              <h3>{editingUser ? 'Edit User Information' : 'Add New User'}</h3>
              <button className="modal-close" onClick={() => setShowUserModal(false)}>
                <X size={20} />
              </button>
            </div>
            
            <div className="modal-body">
              <h4 style={{ marginBottom: '15px', color: '#1a656e' }}>Basic Information</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginBottom: '25px' }}>
                <div className="form-group">
                  <label>First Name</label>
                  <input
                    type="text"
                    name="first_name"
                    value={userFormData.first_name}
                    onChange={handleUserFormChange}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Last Name</label>
                  <input
                    type="text"
                    name="last_name"
                    value={userFormData.last_name}
                    onChange={handleUserFormChange}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Username</label>
                  <input
                    type="text"
                    name="username"
                    value={userFormData.username}
                    onChange={handleUserFormChange}
                    required
                    disabled={!!editingUser} // Disable username for existing users
                  />
                </div>
                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    name="email"
                    value={userFormData.email}
                    onChange={handleUserFormChange}
                    required
                    disabled={!!editingUser} // Disable email for existing users
                  />
                </div>
                <div className="form-group">
                  <label>Role</label>
                  <select
                    name="role"
                    value={userFormData.role}
                    onChange={handleUserFormChange}
                  >
                    <option value="tenant">Tenant</option>
                    <option value="owner">Property Owner</option>
                    <option value="agent">Real Estate Agent</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Gender</label>
                  <select
                    name="gender"
                    value={userFormData.gender}
                    onChange={handleUserFormChange}
                  >
                    <option value="">Select Gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>

              <h4 style={{ marginBottom: '15px', color: '#1a656e' }}>Contact Information</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginBottom: '25px' }}>
                <div className="form-group">
                  <label>Primary Phone</label>
                  <input
                    type="tel"
                    name="contact_number"
                    value={userFormData.contact_number}
                    onChange={handleUserFormChange}
                    placeholder="+256..."
                  />
                </div>
                <div className="form-group">
                  <label>Alternate Phone</label>
                  <input
                    type="tel"
                    name="alternate_number"
                    value={userFormData.alternate_number}
                    onChange={handleUserFormChange}
                    placeholder="+256..."
                  />
                </div>
                <div className="form-group">
                  <label>Date of Birth</label>
                  <input
                    type="date"
                    name="date_of_birth"
                    value={userFormData.date_of_birth}
                    onChange={handleUserFormChange}
                  />
                </div>
                <div className="form-group">
                  <label>Occupation</label>
                  <input
                    type="text"
                    name="occupation"
                    value={userFormData.occupation}
                    onChange={handleUserFormChange}
                    placeholder="Profession"
                  />
                </div>
              </div>

              <h4 style={{ marginBottom: '15px', color: '#1a656e' }}>Professional Information</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginBottom: '25px' }}>
                <div className="form-group">
                  <label>Company Name</label>
                  <input
                    type="text"
                    name="company_name"
                    value={userFormData.company_name}
                    onChange={handleUserFormChange}
                    placeholder="Company (if applicable)"
                  />
                </div>
                <div className="form-group">
                  <label>Annual Income (UGX)</label>
                  <input
                    type="number"
                    name="annual_income"
                    value={userFormData.annual_income}
                    onChange={handleUserFormChange}
                    placeholder="Optional"
                  />
                </div>
              </div>

              <h4 style={{ marginBottom: '15px', color: '#1a656e' }}>Address Information</h4>
              <div className="form-group" style={{ marginBottom: '25px' }}>
                <label>Permanent Address</label>
                <textarea
                  name="permanent_address"
                  value={userFormData.permanent_address}
                  onChange={handleUserFormChange}
                  placeholder="Permanent address"
                  rows="2"
                />
              </div>

              <div className="form-group" style={{ marginBottom: '25px' }}>
                <label>Current Address</label>
                <textarea
                  name="current_address"
                  value={userFormData.current_address}
                  onChange={handleUserFormChange}
                  placeholder="Current address"
                  rows="2"
                />
              </div>

              <h4 style={{ marginBottom: '15px', color: '#1a656e' }}>Emergency Contact</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginBottom: '25px' }}>
                <div className="form-group">
                  <label>Emergency Contact Name</label>
                  <input
                    type="text"
                    name="emergency_contact_name"
                    value={userFormData.emergency_contact_name}
                    onChange={handleUserFormChange}
                    placeholder="Emergency contact name"
                  />
                </div>
                <div className="form-group">
                  <label>Emergency Contact Number</label>
                  <input
                    type="tel"
                    name="emergency_contact_number"
                    value={userFormData.emergency_contact_number}
                    onChange={handleUserFormChange}
                    placeholder="Emergency contact phone"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Relationship</label>
                <input
                  type="text"
                  name="emergency_contact_relation"
                  value={userFormData.emergency_contact_relation}
                  onChange={handleUserFormChange}
                  placeholder="e.g., Parent, Spouse, Sibling"
                />
              </div>
            </div>
            
            <div className="form-actions">
              <button className="btn-secondary" onClick={() => setShowUserModal(false)}>
                Cancel
              </button>
              <button className="btn-primary" onClick={handleSaveUser}>
                <Save size={16} />
                {editingUser ? 'Update User' : 'Create User'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Property Owner Registration Modal */}
      {showOwnerModal && (
        <div className="modal-overlay">
          <div className="modal" style={{ maxWidth: '900px', width: '95%', maxHeight: '90vh', overflowY: 'auto' }}>
            <div className="modal-header">
              <h3>Register Property Owner</h3>
              <button className="modal-close" onClick={() => setShowOwnerModal(false)}>
                <X size={20} />
              </button>
            </div>
            
            <div className="modal-body">
              {/* Profile Picture Upload */}
              <div className="form-group">
                <label>Profile Picture *</label>
                <div className="file-upload-container">
                  <div className="file-upload-preview">
                    {ownerProfilePreview ? (
                      <img src={ownerProfilePreview} alt="Profile Preview" className="preview-image" />
                    ) : (
                      <div className="preview-placeholder">
                        <span>📷</span>
                        <p>No profile picture selected</p>
                      </div>
                    )}
                  </div>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleOwnerProfilePictureChange}
                    className="file-input"
                    required
                  />
                  <button type="button" className="file-upload-btn" onClick={() => document.querySelector('.file-input').click()}>
                    Choose Profile Picture
                  </button>
                </div>
              </div>

              {/* National ID Card Upload */}
              <div className="form-group">
                <label>National ID Card *</label>
                <div className="file-upload-container">
                  <div className="file-upload-preview">
                    {ownerIdPreview ? (
                      <img src={ownerIdPreview} alt="ID Card Preview" className="preview-image id-preview" />
                    ) : (
                      <div className="preview-placeholder">
                        <span>🆔</span>
                        <p>No ID card selected</p>
                      </div>
                    )}
                  </div>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleOwnerNationalIdChange}
                    className="file-input"
                    required
                  />
                  <button type="button" className="file-upload-btn" onClick={() => document.querySelectorAll('.file-input')[1].click()}>
                    Choose National ID Card
                  </button>
                </div>
              </div>

              <h4 style={{ marginBottom: '15px', color: '#1a656e' }}>Basic Information</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginBottom: '25px' }}>
                <div className="form-group">
                  <label>First Name</label>
                  <input
                    type="text"
                    name="first_name"
                    value={ownerFormData.first_name}
                    onChange={handleOwnerFormChange}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Last Name</label>
                  <input
                    type="text"
                    name="last_name"
                    value={ownerFormData.last_name}
                    onChange={handleOwnerFormChange}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    name="email"
                    value={ownerFormData.email}
                    onChange={handleOwnerFormChange}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Role</label>
                  <select
                    name="role"
                    value={ownerFormData.role}
                    onChange={handleOwnerFormChange}
                  >
                    <option value="owner">Property Owner</option>
                    <option value="agent">Real Estate Agent</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Gender</label>
                  <select
                    name="gender"
                    value={ownerFormData.gender}
                    onChange={handleOwnerFormChange}
                  >
                    <option value="">Select Gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>

              <h4 style={{ marginBottom: '15px', color: '#1a656e' }}>Contact Information</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginBottom: '25px' }}>
                <div className="form-group">
                  <label>Primary Phone</label>
                  <input
                    type="tel"
                    name="contact_number"
                    value={ownerFormData.contact_number}
                    onChange={handleOwnerFormChange}
                    placeholder="+256..."
                  />
                </div>
                <div className="form-group">
                  <label>Alternate Phone</label>
                  <input
                    type="tel"
                    name="alternate_number"
                    value={ownerFormData.alternate_number}
                    onChange={handleOwnerFormChange}
                    placeholder="+256..."
                  />
                </div>
                <div className="form-group">
                  <label>Date of Birth</label>
                  <input
                    type="date"
                    name="date_of_birth"
                    value={ownerFormData.date_of_birth}
                    onChange={handleOwnerFormChange}
                  />
                </div>
                <div className="form-group">
                  <label>Occupation</label>
                  <input
                    type="text"
                    name="occupation"
                    value={ownerFormData.occupation}
                    onChange={handleOwnerFormChange}
                    placeholder="Profession"
                  />
                </div>
              </div>

              <h4 style={{ marginBottom: '15px', color: '#1a656e' }}>Professional Information</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginBottom: '25px' }}>
                <div className="form-group">
                  <label>Company Name</label>
                  <input
                    type="text"
                    name="company_name"
                    value={ownerFormData.company_name}
                    onChange={handleOwnerFormChange}
                    placeholder="Company (if applicable)"
                  />
                </div>
                <div className="form-group">
                  <label>Annual Income (UGX)</label>
                  <input
                    type="number"
                    name="annual_income"
                    value={ownerFormData.annual_income}
                    onChange={handleOwnerFormChange}
                    placeholder="Optional"
                  />
                </div>
              </div>

              <h4 style={{ marginBottom: '15px', color: '#1a656e' }}>Address Information</h4>
              <div className="form-group" style={{ marginBottom: '25px' }}>
                <label>Permanent Address</label>
                <textarea
                  name="permanent_address"
                  value={ownerFormData.permanent_address}
                  onChange={handleOwnerFormChange}
                  placeholder="Permanent address"
                  rows="2"
                />
              </div>

              <div className="form-group" style={{ marginBottom: '25px' }}>
                <label>Current Address</label>
                <textarea
                  name="current_address"
                  value={ownerFormData.current_address}
                  onChange={handleOwnerFormChange}
                  placeholder="Current address"
                  rows="2"
                />
              </div>

              <h4 style={{ marginBottom: '15px', color: '#1a656e' }}>Emergency Contact</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginBottom: '25px' }}>
                <div className="form-group">
                  <label>Emergency Contact Name</label>
                  <input
                    type="text"
                    name="emergency_contact_name"
                    value={ownerFormData.emergency_contact_name}
                    onChange={handleOwnerFormChange}
                    placeholder="Emergency contact name"
                  />
                </div>
                <div className="form-group">
                  <label>Emergency Contact Number</label>
                  <input
                    type="tel"
                    name="emergency_contact_number"
                    value={ownerFormData.emergency_contact_number}
                    onChange={handleOwnerFormChange}
                    placeholder="Emergency contact phone"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Relationship</label>
                <input
                  type="text"
                  name="emergency_contact_relation"
                  value={ownerFormData.emergency_contact_relation}
                  onChange={handleOwnerFormChange}
                  placeholder="e.g., Parent, Spouse, Sibling"
                />
              </div>
            </div>
            
            <div className="form-actions">
              <button className="btn-secondary" onClick={() => setShowOwnerModal(false)}>
                Cancel
              </button>
              <button className="btn-primary" onClick={handleSaveOwner}>
                <Save size={16} />
                Register Property Owner
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
