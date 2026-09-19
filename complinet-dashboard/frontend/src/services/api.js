import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchSummary = async () => {
  const response = await apiClient.get('/compliance/summary');
  return response.data;
};

export const fetchDevices = async () => {
  const response = await apiClient.get('/compliance/devices');
  return response.data;
};

export const fetchRules = async () => {
  const response = await apiClient.get('/compliance/rules');
  return response.data;
};

export const triggerAuditRun = async () => {
  const response = await apiClient.post('/compliance/run');
  return response.data;
};

export const createDevice = async (deviceData) => {
  const response = await apiClient.post('/devices/', deviceData);
  return response.data;
};

export const fetchSystemHealth = async () => {
  const response = await apiClient.get('/system/health');
  return response.data;
};

export const fetchAuditEvents = async () => {
  const response = await apiClient.get('/audit/events');
  return response.data;
};

export const fetchRemediationRequests = async () => {
  const response = await apiClient.get('/remediation/requests');
  return response.data;
};

export const createRemediationRequest = async (request) => {
  const response = await apiClient.post('/remediation/requests', request);
  return response.data;
};

export const approveRemediationRequest = async (requestId, approvedBy) => {
  const response = await apiClient.post(`/remediation/requests/${requestId}/approve`, {
    approved_by: approvedBy,
  });
  return response.data;
};

export const executeRemediationRequest = async (requestId) => {
  const response = await apiClient.post(`/remediation/requests/${requestId}/execute`);
  return response.data;
};

