import { useState, useEffect, useContext, createContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { authAPI, handleAPIError } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [role, setRole] = useState(null);
  const navigate = useNavigate();

  // Check authentication status on mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const storedUser = localStorage.getItem('user');
      const token = localStorage.getItem('auth_token');

      if (storedUser && token) {
        const userData = JSON.parse(storedUser);
        setUser(userData);
        setIsAuthenticated(true);
        setRole(userData.role);

        // Verify with server
        const response = await authAPI.checkAuth();
        if (response.success && response.data.authenticated) {
          setUser(response.data.user);
          setRole(response.data.user.role);
          localStorage.setItem('user', JSON.stringify(response.data.user));
        } else {
          // Server says not authenticated, clear local storage
          clearAuth();
        }
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      clearAuth();
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
      setIsLoading(true);
      const response = await authAPI.login(credentials);

      if (response.success) {
        const userData = response.data;
        setUser(userData);
        setIsAuthenticated(true);
        setRole(userData.role);

        // Store in localStorage
        localStorage.setItem('user', JSON.stringify(userData));
        localStorage.setItem('auth_token', 'session-token'); // Using session-based auth

        toast.success('Login successful!');

        // Redirect based on role
        if (userData.role === 'police') {
          navigate('/police/dashboard');
        } else {
          navigate('/public/dashboard');
        }

        return { success: true, user: userData };
      } else {
        toast.error(response.error || 'Login failed');
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorInfo = handleAPIError(error);
      toast.error(errorInfo.message);
      return { success: false, error: errorInfo.message };
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setIsLoading(true);
      const response = await authAPI.register(userData);

      if (response.success) {
        const newUserData = response.data;
        setUser(newUserData);
        setIsAuthenticated(true);
        setRole(newUserData.role);

        // Store in localStorage
        localStorage.setItem('user', JSON.stringify(newUserData));
        localStorage.setItem('auth_token', 'session-token');

        toast.success('Registration successful!');

        // Redirect based on role
        if (newUserData.role === 'police') {
          navigate('/police/dashboard');
        } else {
          navigate('/public/dashboard');
        }

        return { success: true, user: newUserData };
      } else {
        toast.error(response.error || 'Registration failed');
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorInfo = handleAPIError(error);
      toast.error(errorInfo.message);
      return { success: false, error: errorInfo.message };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      clearAuth();
      toast.success('Logged out successfully');
      navigate('/login');
    }
  };

  const updateProfile = async (profileData) => {
    try {
      setIsLoading(true);
      const response = await authAPI.updateProfile(profileData);

      if (response.success) {
        const updatedUserData = response.data;
        setUser(updatedUserData);
        localStorage.setItem('user', JSON.stringify(updatedUserData));
        toast.success('Profile updated successfully!');
        return { success: true, user: updatedUserData };
      } else {
        toast.error(response.error || 'Profile update failed');
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorInfo = handleAPIError(error);
      toast.error(errorInfo.message);
      return { success: false, error: errorInfo.message };
    } finally {
      setIsLoading(false);
    }
  };

  const changePassword = async (passwordData) => {
    try {
      setIsLoading(true);
      const response = await authAPI.changePassword(passwordData);

      if (response.success) {
        toast.success('Password changed successfully!');
        return { success: true };
      } else {
        toast.error(response.error || 'Password change failed');
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorInfo = handleAPIError(error);
      toast.error(errorInfo.message);
      return { success: false, error: errorInfo.message };
    } finally {
      setIsLoading(false);
    }
  };

  const deleteAccount = async (password) => {
    try {
      setIsLoading(true);
      const response = await authAPI.deleteAccount(password);

      if (response.success) {
        clearAuth();
        toast.success('Account deleted successfully');
        navigate('/login');
        return { success: true };
      } else {
        toast.error(response.error || 'Account deletion failed');
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorInfo = handleAPIError(error);
      toast.error(errorInfo.message);
      return { success: false, error: errorInfo.message };
    } finally {
      setIsLoading(false);
    }
  };

  const clearAuth = () => {
    setUser(null);
    setIsAuthenticated(false);
    setRole(null);
    localStorage.removeItem('user');
    localStorage.removeItem('auth_token');
  };

  // Role-based helper functions
  const isPolice = () => role === 'police';
  const isPublic = () => role === 'public';

  // Get role information
  const getRoleInfo = async () => {
    try {
      const response = await authAPI.getRoleInfo();
      if (response.success) {
        return response.data;
      }
      return null;
    } catch (error) {
      console.error('Failed to get role info:', error);
      return null;
    }
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    role,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    deleteAccount,
    clearAuth,
    isPolice,
    isPublic,
    getRoleInfo,
    checkAuthStatus,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Protected route component
export const ProtectedRoute = ({ children, requiredRole = null }) => {
  const { isAuthenticated, isLoading, role } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) {
        navigate('/login');
        return;
      }

      if (requiredRole && role !== requiredRole) {
        // Redirect to appropriate dashboard based on role
        if (role === 'police') {
          navigate('/police/dashboard');
        } else {
          navigate('/public/dashboard');
        }
        return;
      }
    }
  }, [isAuthenticated, isLoading, role, requiredRole, navigate]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect in useEffect
  }

  if (requiredRole && role !== requiredRole) {
    return null; // Will redirect in useEffect
  }

  return children;
};

// Public route component (redirect if authenticated)
export const PublicRoute = ({ children }) => {
  const { isAuthenticated, isLoading, role } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      // Redirect based on role
      if (role === 'police') {
        navigate('/police/dashboard');
      } else {
        navigate('/public/dashboard');
      }
    }
  }, [isAuthenticated, isLoading, role, navigate]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (isAuthenticated) {
    return null; // Will redirect in useEffect
  }

  return children;
};