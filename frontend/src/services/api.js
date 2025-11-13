import axios from 'axios';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add authentication token if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle common errors
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear local storage and redirect to login
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    } else if (error.response?.status === 403) {
      // Forbidden - user doesn't have permission
      console.error('Access forbidden:', error.response.data);
    } else if (error.response?.status >= 500) {
      // Server error
      console.error('Server error:', error.response.data);
    }

    return Promise.reject(error);
  }
);

// Authentication API calls
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: (userData) => api.put('/auth/profile', userData),
  changePassword: (passwordData) => api.post('/auth/change-password', passwordData),
  checkAuth: () => api.get('/auth/check-auth'),
  getRoleInfo: () => api.get('/auth/role-info'),
  deleteAccount: (password) => api.delete('/auth/delete-account', { data: { password } }),
};

// FIR API calls (Police Portal)
export const firAPI = {
  getFirs: (params = {}) => api.get('/police/fir', { params }),
  createFir: (firData) => api.post('/police/fir', firData),
  getFir: (firId) => api.get(`/police/fir/${firId}`),
  updateFir: (firId, firData) => api.put(`/police/fir/${firId}`, firData),
  deleteFir: (firId) => api.delete(`/police/fir/${firId}`),
  submitFir: (firId) => api.post(`/police/fir/${firId}/submit`),
  archiveFir: (firId) => api.post(`/police/fir/${firId}/archive`),
  searchFirs: (searchParams) => api.get('/police/fir/search', { params: searchParams }),
  getFirStats: () => api.get('/police/fir/stats'),
  generateFirPDF: (firId) => api.post(`/police/fir/${firId}/generate-pdf`),
};

// Legal Search API calls
export const legalAPI = {
  searchLegalActs: (searchParams) => api.get('/legal/search', { params: searchParams }),
  getLegalSection: (actName, sectionNumber) =>
    api.get(`/legal/section/${encodeURIComponent(actName)}/${encodeURIComponent(sectionNumber)}`),
  getLegalSectionById: (sectionId) => api.get(`/legal/section/${sectionId}`),
  getLegalActs: () => api.get('/legal/acts'),
  getActSections: (actName, params = {}) =>
    api.get(`/legal/act/${encodeURIComponent(actName)}/sections`, { params }),
  getLegalCategories: () => api.get('/legal/categories'),
  analyzeText: (text) => api.post('/legal/analyze', { text }),
  getPopularSections: () => api.get('/legal/popular'),
};

// Complaint API calls (Public Portal)
export const complaintAPI = {
  getComplaints: (params = {}) => api.get('/public/complaint', { params }),
  createComplaint: (complaintData) => api.post('/public/complaint', complaintData),
  getComplaint: (complaintId) => api.get(`/public/complaint/${complaintId}`),
  updateComplaint: (complaintId, complaintData) =>
    api.put(`/public/complaint/${complaintId}`, complaintData),
  deleteComplaint: (complaintId) => api.delete(`/public/complaint/${complaintId}`),
  formatComplaint: (complaintId) => api.post(`/public/complaint/${complaintId}/format`),
  archiveComplaint: (complaintId) => api.post(`/public/complaint/${complaintId}/archive`),
  searchComplaints: (searchParams) => api.get('/public/complaint/search', { params: searchParams }),
  getComplaintStats: () => api.get('/public/complaint/stats'),
  getComplaintCategories: () => api.get('/public/complaint/categories'),
};

// File Upload API calls
export const uploadAPI = {
  uploadEvidence: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload/evidence', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  uploadMultipleFiles: (files) => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });
    return api.post('/upload/batch', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  downloadEvidence: (filename) =>
    api.get(`/upload/evidence/${encodeURIComponent(filename)}`, {
      responseType: 'blob',
    }),
  deleteEvidence: (filename) =>
    api.delete(`/upload/evidence/${encodeURIComponent(filename)}`),
  getFileInfo: (filename) =>
    api.get(`/upload/evidence/${encodeURIComponent(filename)}/info`),
  getUploadStats: () => api.get('/upload/stats'),
  cleanupOrphanedFiles: () => api.post('/upload/cleanup'),
};

// Utility functions for error handling
export const handleAPIError = (error) => {
  if (error.response) {
    // Server responded with error status
    return {
      message: error.response.data?.error || 'Server error occurred',
      status: error.response.status,
      details: error.response.data?.details,
    };
  } else if (error.request) {
    // Request was made but no response received
    return {
      message: 'Network error. Please check your connection.',
      status: null,
    };
  } else {
    // Something else happened
    return {
      message: error.message || 'An unexpected error occurred',
      status: null,
    };
  }
};

// Utility function for API response handling
export const handleAPIResponse = (response) => {
  if (response.success) {
    return {
      success: true,
      data: response.data,
      message: response.message,
    };
  } else {
    return {
      success: false,
      error: response.error,
      details: response.details,
    };
  }
};

// File download utility
export const downloadFile = (blob, filename) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

// File validation utility
export const validateFile = (file, maxSize = 50 * 1024 * 1024, allowedTypes = []) => {
  const errors = [];

  if (file.size > maxSize) {
    errors.push(`File size exceeds maximum limit of ${Math.round(maxSize / (1024 * 1024))}MB`);
  }

  if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
    errors.push(`File type ${file.type} is not allowed`);
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

export default api;