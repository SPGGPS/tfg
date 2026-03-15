import axios from 'axios';

// Configure axios defaults
axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/v1';

// Add auth token to requests (placeholder for now)
axios.interceptors.request.use((config) => {
  // TODO: Add JWT token when authentication is implemented
  // const token = sessionStorage.getItem('tfg_token');
  // if (token) {
  //   config.headers.Authorization = `Bearer ${token}`;
  // }
  return config;
});

// Assets API
export const assetsApi = {
  getAssets: (params) => axios.get('/assets', { params }),
  bulkAssignTags: (data) => axios.post('/assets/bulk-tags', data),
};

// Tags API
export const tagsApi = {
  getTags: (params) => axios.get('/tags', { params }),
  createTag: (data) => axios.post('/tags', data),
  updateTag: (id, data) => axios.put(`/tags/${id}`, data),
  deleteTag: (id) => axios.delete(`/tags/${id}`),
};

// Audit API
export const auditApi = {
  getAuditLogs: (params) => axios.get('/audit-logs', { params }),
};

// Auth API
export const authApi = {
  getOidcConfig: () => axios.get('/auth/oidc/config'),
  validateToken: (token) => axios.post('/auth/validate-token', { token }),
};

// Health check
export const healthApi = {
  check: () => axios.get('/healthz'),
};

export default axios;