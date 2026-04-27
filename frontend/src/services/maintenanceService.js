import api from '../api/axios';

const maintenanceService = {
  // Categories
  getCategories: () => api.get('/maintenance/categories/'),
  
  // Maintenance Requests
  getRequests: (params = {}) => api.get('/maintenance/requests/', { params }),
  getRequest: (id) => api.get(`/maintenance/requests/${id}/`),
  createRequest: (data) => api.post('/maintenance/requests/', data),
  updateRequest: (id, data) => api.patch(`/maintenance/requests/${id}/`, data),
  deleteRequest: (id) => api.delete(`/maintenance/requests/${id}/`),
  assignRequest: (id, assignedTo) => api.post(`/maintenance/requests/${id}/assign/`, { assigned_to: assignedTo }),
  getMyRequests: (params = {}) => api.get('/maintenance/requests/my/', { params }),
  
  // Images
  getImages: (requestId) => api.get(`/maintenance/requests/${requestId}/images/`),
  uploadImage: (requestId, formData) => api.post(`/maintenance/requests/${requestId}/images/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  deleteImage: (imageId) => api.delete(`/maintenance/images/${imageId}/`),
  
  // Comments
  getComments: (requestId) => api.get(`/maintenance/requests/${requestId}/comments/`),
  addComment: (requestId, data) => api.post(`/maintenance/requests/${requestId}/comments/`, data),
  updateComment: (commentId, data) => api.patch(`/maintenance/comments/${commentId}/`, data),
  deleteComment: (commentId) => api.delete(`/maintenance/comments/${commentId}/`),
  
  // History
  getHistory: (requestId) => api.get(`/maintenance/requests/${requestId}/history/`),
  
  // Statistics
  getStats: () => api.get('/maintenance/stats/'),
};

export default maintenanceService;
