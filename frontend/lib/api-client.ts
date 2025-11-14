import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API endpoints
export const api = {
  // Auth
  login: (username: string, password: string) =>
    apiClient.post('/api/auth/token', { username, password }),
  
  register: (data: any) =>
    apiClient.post('/api/auth/register', data),
  
  // Dashboard
  getDashboard: (projectId?: string) =>
    apiClient.get('/api/analytics/dashboard', { params: { project_id: projectId } }),
  
  // Projects
  getProjects: () =>
    apiClient.get('/api/reports/projects'),
  
  getProject: (id: string) =>
    apiClient.get(`/api/reports/projects/${id}`),
  
  createProject: (data: any) =>
    apiClient.post('/api/reports/projects', data),
  
  // Test Results
  getTestHistory: (historyId: string) =>
    apiClient.get(`/api/reports/tests/${historyId}/history`),
  
  // AI Analysis
  performRCA: (testResultId: string) =>
    apiClient.post('/api/ai/analyze/rca', { test_result_id: testResultId }),
  
  detectFlakyTests: (projectId: string, timeWindowDays: number = 30) =>
    apiClient.post('/api/ai/analyze/flaky', {
      project_id: projectId,
      time_window_days: timeWindowDays,
    }),
  
  queryNL: (query: string, projectId?: string) =>
    apiClient.post('/api/ai/query/nl', { query, project_id: projectId }),
  
  // Analytics
  getProjectStats: (projectId: string) =>
    apiClient.get(`/api/analytics/projects/${projectId}/stats`),
  
  getProjectTrends: (projectId: string, period: string = '30d') =>
    apiClient.get(`/api/analytics/projects/${projectId}/trends`, { params: { period } }),
  
  // Upload
  uploadReport: (formData: FormData) =>
    apiClient.post('/api/reports/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
};

