import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import api from '../services/api';

export interface User {
  id: string;
  name: string;
  email: string;
  isGuest: boolean;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Verify token and get user data on startup
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('nirvami_auth_token');
      
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        // Verify token and get user data from backend
        const userData = await api.getCurrentUser();
        setUser({
          id: userData.id,
          name: userData.name || userData.email.split('@')[0],
          email: userData.email,
          isGuest: false
        });
      } catch (error) {
        console.error('Token validation failed:', error);
        // Invalid token - clear it
        localStorage.removeItem('nirvami_auth_token');
        localStorage.removeItem('nirvami_user');
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await api.login({ email, password });
      
      // Store token
      localStorage.setItem('nirvami_auth_token', response.access_token);
      
      // Set user from response
      setUser({
        id: response.user.id,
        name: response.user.name || email.split('@')[0],
        email: response.user.email,
        isGuest: false
      });
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const register = async (name: string, email: string, password: string) => {
    try {
      const response = await api.register({ name, email, password });
      
      // Store token
      localStorage.setItem('nirvami_auth_token', response.access_token);
      
      // Set user from response
      setUser({
        id: response.user.id,
        name: response.user.name || name,
        email: response.user.email,
        isGuest: false
      });
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('nirvami_auth_token');
    localStorage.removeItem('nirvami_user');
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      const userData = await api.getCurrentUser();
      setUser({
        id: userData.id,
        name: userData.name || userData.email.split('@')[0],
        email: userData.email,
        isGuest: false
      });
    } catch (error) {
      console.error('Failed to refresh user:', error);
      logout();
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        refreshUser
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
