import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'community_manager' | 'trader' | 'producer' | 'consumer';
  communityId?: string;
  profilePicture?: string;
  isVerified: boolean;
  createdAt: string;
  lastLoginAt?: string;
}

export interface Permission {
  id: string;
  name: string;
  description: string;
  resource: string;
  action: string;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  permissions: Permission[];
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (userData: RegisterData) => Promise<void>;
  updateProfile: (userData: Partial<User>) => Promise<void>;
  hasPermission: (resource: string, action: string) => boolean;
  isRole: (role: string) => boolean;
  refreshUser: () => Promise<void>;
}

export interface RegisterData {
  name: string;
  email: string;
  password: string;
  role: 'trader' | 'producer' | 'consumer';
  communityId?: string;
}

export interface LoginResponse {
  user: User;
  token: string;
  permissions: Permission[];
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Update apiCall to support PUT method
  const apiCall = async (url: string, method: 'GET' | 'POST' | 'PUT' = 'GET', data?: any) => {
    const baseUrl = 'http://localhost:8000';
    const fullUrl = `${baseUrl}${url.startsWith('/') ? url : `/${url}`}`;
    
    const config: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      ...(data && { body: JSON.stringify(data) }),
    };

    const response = await fetch(fullUrl, config);
    if (!response.ok) {
      throw new Error(`API call failed: ${response.statusText}`);
    }
    return response.json();
  };

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedToken = localStorage.getItem('powershare_token');
        const storedUser = localStorage.getItem('powershare_user');
        
        if (storedToken && storedUser) {
          setToken(storedToken);
          setUser(JSON.parse(storedUser));
          
          // Verify token and refresh user data
          await refreshUser();
        }
      } catch (err) {
        console.error('Failed to initialize auth:', err);
        // Clear invalid stored data
        localStorage.removeItem('powershare_token');
        localStorage.removeItem('powershare_user');
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiCall('/auth/login', 'POST', {
        email,
        password
      }) as LoginResponse;

      const { user: userData, token: authToken, permissions: userPermissions } = response;
      
      setUser(userData);
      setToken(authToken);
      setPermissions(userPermissions);
      
      // Store in localStorage
      localStorage.setItem('powershare_token', authToken);
      localStorage.setItem('powershare_user', JSON.stringify(userData));
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData: RegisterData): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiCall('/auth/register', 'POST', userData) as LoginResponse;
      
      const { user: newUser, token: authToken, permissions: userPermissions } = response;
      
      setUser(newUser);
      setToken(authToken);
      setPermissions(userPermissions);
      
      // Store in localStorage
      localStorage.setItem('powershare_token', authToken);
      localStorage.setItem('powershare_user', JSON.stringify(newUser));
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    setPermissions([]);
    setError(null);
    
    // Clear localStorage
    localStorage.removeItem('powershare_token');
    localStorage.removeItem('powershare_user');
  };

  const updateProfile = async (userData: Partial<User>): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      
      if (!user) throw new Error('No user logged in');
      
      const response = await apiCall(`/auth/profile/${user.id}`, 'PUT', userData) as User;
      
      const updatedUser = response;
      setUser(updatedUser);
      
      // Update localStorage
      localStorage.setItem('powershare_user', JSON.stringify(updatedUser));
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Profile update failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const refreshUser = async (): Promise<void> => {
    try {
      if (!token) return;
      
      const response = await apiCall('/auth/me', 'GET') as { user: User; permissions: Permission[] };
      
      const { user: userData, permissions: userPermissions } = response;
      
      setUser(userData);
      setPermissions(userPermissions);
      
      // Update localStorage
      localStorage.setItem('powershare_user', JSON.stringify(userData));
      
    } catch (err: any) {
      console.error('Failed to refresh user:', err);
      // If refresh fails, logout user
      logout();
    }
  };

  const hasPermission = (resource: string, action: string): boolean => {
    return permissions.some(
      permission => permission.resource === resource && permission.action === action
    );
  };

  const isRole = (role: string): boolean => {
    return user?.role === role;
  };

  const value: AuthContextType = {
    user,
    token,
    permissions,
    loading,
    error,
    login,
    logout,
    register,
    updateProfile,
    hasPermission,
    isRole,
    refreshUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};