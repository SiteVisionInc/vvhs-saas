// frontend/src/contexts/AuthContext.tsx
import React, { createContext, useState, useContext, useEffect } from 'react';
import { api } from '../services/api';
import { User } from '../types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User | null) => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in (has token)
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          api.loadToken(); // Make sure API has the token
          const currentUser = await api.getCurrentUser();
          setUser(currentUser);
        } catch (error) {
          console.error('Failed to get current user:', error);
          localStorage.removeItem('token');
          localStorage.removeItem('refresh_token');
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (username: string, password: string) => {
    try {
      // Call API login
      const tokenResponse = await api.login({ username, password });
      
      // Get user profile
      const currentUser = await api.getCurrentUser();
      
      // Set user in context
      setUser(currentUser);
    } catch (error) {
      console.error('Login failed in AuthContext:', error);
      throw error;
    }
  };

  const logout = () => {
    api.logout();
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
  };

  const value: AuthContextType = {
    user,
    loading,
    login,
    logout,
    setUser,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};