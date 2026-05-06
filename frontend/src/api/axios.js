import axios from 'axios';

// Function to get CSRF token from cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Use production API URL for Vercel deployment
const getApiBaseUrl = () => {
  // Check if we're in production (Vercel)
  if (import.meta.env.PROD) {
    return 'https://nestoria-5j25.onrender.com/api';
  }
  // Use environment variable if available (for local development)
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  // Fallback to localhost or local network IP
  return `http://${window.location.hostname}:8001/api`;
};

const api = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

api.interceptors.request.use(
  (config) => {
    // Skip adding Authorization header for login/register requests
    const skipAuth = config.url?.includes('/login/') || config.url?.includes('/register/');
    
    if (!skipAuth) {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    
    // Only add CSRF token for non-get requests to endpoints that need it
    // Skip CSRF for login/register as they use JWT
    // Also skip CSRF for cancel booking endpoint
    const skipCSRF = config.url?.includes('/login/') || 
                     config.url?.includes('/register/') || 
                     config.url?.includes('/cancel/');
    
    if (!skipCSRF && ['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase())) {
      const csrfToken = getCookie('csrftoken');
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
      }
    }
    
    console.log('Request config:', {
      method: config.method,
      url: config.url,
      headers: config.headers,
      data: config.data
    });
    
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
