import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { registerUser, loginUser, fetchCurrentUser } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('auth_token'));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const clearError = () => setError(null);

  // Validate existing token on initial application load
  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem('auth_token');
      if (savedToken) {
        try {
          const userData = await fetchCurrentUser(savedToken);
          setUser(userData);
          setToken(savedToken);
        } catch (err) {
          console.warn('Session expired or invalid token:', err.message);
          localStorage.removeItem('auth_token');
          setToken(null);
          setUser(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = useCallback(async (email, password) => {
    setError(null);
    try {
      const data = await loginUser(email, password);
      localStorage.setItem('auth_token', data.access_token);
      setToken(data.access_token);
      setUser(data.user);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, []);

  const register = useCallback(async (name, email, password) => {
    setError(null);
    try {
      const data = await registerUser(name, email, password);
      localStorage.setItem('auth_token', data.access_token);
      setToken(data.access_token);
      setUser(data.user);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('auth_token');
    setToken(null);
    setUser(null);
    setError(null);
  }, []);

  const value = {
    user,
    token,
    isAuthenticated: !!user,
    loading,
    error,
    clearError,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
