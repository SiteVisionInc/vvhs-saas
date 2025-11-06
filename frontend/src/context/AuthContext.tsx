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
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          // Ensure API has the token loaded
          api.setToken(token);
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
      // Step 1: Call login and get token
      console.log('Step 1: Calling API login...');
      const tokenResponse = await api.login({ username, password });
      console.log('Step 1 complete: Token received');
      
      // Step 2: Token is already set by api.login(), now get user
      // Add a small delay to ensure token is propagated
      await new Promise(resolve => setTimeout(resolve, 100));
      
      console.log('Step 2: Getting user profile...');
      const currentUser = await api.getCurrentUser();
      console.log('Step 2 complete: User retrieved:', currentUser);
      
      // Step 3: Set user in context
      setUser(currentUser);
      console.log('Login flow complete');
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