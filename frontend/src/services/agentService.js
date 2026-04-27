import api from '../api/axios';

const agentService = {
  // Agent Profiles
  getAgents: (params = {}) => api.get('/agents/profiles/', { params }),
  
  // Agent Requests
  getRequests: (params = {}) => api.get('/agents/requests/', { params }),
  createRequest: (data) => api.post('/agents/requests/', data),
  updateRequest: (id, data) => api.patch(`/agents/requests/${id}/`, data),
  
  // Statistics
  getStatistics: () => api.get('/agents/statistics/'),
  
  // Manual Assignment (Admin only)
  assignAgent: (requestId, agentId) => api.post(`/agents/assign/${requestId}/`, { agent_id: agentId }),
};

export default agentService;
