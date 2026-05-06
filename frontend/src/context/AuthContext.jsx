import React, { createContext, useState, useEffect } from 'react';
import api from '../api/axios';

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        // Check if user is authenticated by calling profile endpoint
        const res = await api.get('/accounts/profile/');
        if (res.data) {
          setUser(res.data);
          // Update localStorage with fresh user data
          localStorage.setItem('user', JSON.stringify(res.data));
        }
      } catch (error) {
        console.log('User not authenticated:', error.response?.status || error.message);
        // Fallback to localStorage if API call fails
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
          try {
            const user = JSON.parse(storedUser);
            setUser(user);
          } catch {
            localStorage.removeItem('user');
            setUser(null);
          }
        } else {
          setUser(null);
        }
      } finally {
        setLoading(false);
      }
    };
    
    // Add a timeout to prevent infinite loading
    const timeout = setTimeout(() => {
      setLoading(false);
    }, 5000);
    
    checkAuthStatus();
    
    return () => clearTimeout(timeout);
  }, []);

  const login = async (email, password) => {
    console.log('Attempting login with:', { email, password });
    console.log('Request payload:', { username: email, password });
    
    // Clear any existing tokens before attempting login
    localStorage.removeItem('token');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    
    try {
      const res = await api.post('/accounts/login/', { username: email, password });
      console.log('Login response:', res.data); // Debug log
      
      if (res.data.user) {
        setUser(res.data.user);
        // Store user data in localStorage as fallback
        localStorage.setItem('user', JSON.stringify(res.data.user));
        
        // Store authentication tokens in localStorage
        if (res.data.access && res.data.refresh) {
          localStorage.setItem('token', res.data.access);
          localStorage.setItem('access_token', res.data.access);
          localStorage.setItem('refresh_token', res.data.refresh);
          console.log('Access token stored:', res.data.access);
          console.log('Refresh token stored:', res.data.refresh);
        } else {
          console.log('No tokens found in response');
          Object.keys(res.data).forEach(key => {
            console.log(`${key}:`, res.data[key]);
          });
        }
      }
      return res.data;
    } catch (error) {
      console.error('Login error details:', error.response?.data);
      console.error('Login error status:', error.response?.status);
      console.error('Login error headers:', error.response?.headers);
      
      // Show more detailed error information
      if (error.response?.data?.non_field_errors) {
        console.error('Non-field errors:', error.response.data.non_field_errors);
      }
      if (error.response?.data?.username) {
        console.error('Username errors:', error.response.data.username);
      }
      if (error.response?.data?.password) {
        console.error('Password errors:', error.response.data.password);
      }
      
      throw error;
    }
  };

  const register = async (userData) => {
    try {
      // Log the data being sent for debugging
      console.log('Registration data being sent:');
      for (let [key, value] of userData.entries()) {
        console.log(`${key}:`, value);
      }
      
      // Set proper headers for FormData
      const config = {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      };
      
      const res = await api.post('/accounts/register/', userData, config);
      return res.data;
    } catch (error) {
      console.error('Registration error details:', error.response?.data);
      console.error('Registration error status:', error.response?.status);
      console.error('Registration error headers:', error.response?.headers);
      
      // Show more detailed error information
      if (error.response?.data) {
        Object.keys(error.response.data).forEach(field => {
          console.error(`${field} errors:`, error.response.data[field]);
        });
      }
      
      throw error;
    }
  };

  const logout = () => {
    setUser(null);
    // Clear localStorage user
    localStorage.removeItem('user');
    // Clear localStorage tokens
    localStorage.removeItem('token');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
