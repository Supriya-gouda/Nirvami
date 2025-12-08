import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import api from '../services/api';

export interface User {
  id: string;
  name: string; // Display name (derived from full_name)
  full_name?: string; // Full name from profile
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
      const cachedUser = localStorage.getItem('nirvami_user');
      
      if (!token) {
        setIsLoading(false);
        return;
      }

      // Use cached user data immediately for faster load
      if (cachedUser) {
        try {
          const parsed = JSON.parse(cachedUser);
          setUser(parsed);
          setIsLoading(false);
          
          // Refresh user data in background if full_name is missing or to verify token
          api.getCurrentUser().then((userData) => {
            const userObj = {
              id: userData.id,
              name: userData.full_name || userData.email.split('@')[0],
              full_name: userData.full_name,
              email: userData.email,
              isGuest: false
            };
            setUser(userObj);
            localStorage.setItem('nirvami_user', JSON.stringify(userObj));
          }).catch((error) => {
            console.error('Background token validation failed:', error);
            localStorage.removeItem('nirvami_auth_token');
            localStorage.removeItem('nirvami_user');
            setUser(null);
          });
          return;
        } catch (e) {
          console.error('Invalid cached user data:', e);
        }
      }

      // No cached user - fetch from backend
      try {
        const userData = await api.getCurrentUser();
        const userObj = {
          id: userData.id,
          name: userData.full_name || userData.email.split('@')[0],
          full_name: userData.full_name,
          email: userData.email,
          isGuest: false
        };
        setUser(userObj);
        localStorage.setItem('nirvami_user', JSON.stringify(userObj));
      } catch (error) {
        console.error('Token validation failed:', error);
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
      // Use Supabase directly for faster login
      const response = await api.loginWithSupabase({ email, password });
      
      // Store token
      localStorage.setItem('nirvami_auth_token', response.access_token);
      
      // Set user from response
      const userObj = {
        id: response.user.id,
        name: response.user.full_name || email.split('@')[0],
        full_name: response.user.full_name,
        email: response.user.email,
        isGuest: false
      };
      setUser(userObj);
      
      // Cache user for faster subsequent loads
      localStorage.setItem('nirvami_user', JSON.stringify(userObj));
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const register = async (name: string, email: string, password: string) => {
    try {
      const response = await api.register({ full_name: name, email, password });
      
      console.log('Registration response:', response);
      
      // Store token
      localStorage.setItem('nirvami_auth_token', response.access_token);
      
      // Set user from response - handle if user is undefined
      if (!response.user) {
        throw new Error('Invalid response from server - user data missing');
      }
      
      const userObj = {
        id: response.user.id,
        name: response.user.full_name || response.user.email?.split('@')[0] || name,
        full_name: response.user.full_name,
        email: response.user.email,
        isGuest: false
      };
      setUser(userObj);
      
      // Cache user for faster subsequent loads
      localStorage.setItem('nirvami_user', JSON.stringify(userObj));
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
      const userObj = {
        id: userData.id,
        name: userData.full_name || userData.email.split('@')[0],
        full_name: userData.full_name,
        email: userData.email,
        isGuest: false
      };
      setUser(userObj);
      localStorage.setItem('nirvami_user', JSON.stringify(userObj));
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
