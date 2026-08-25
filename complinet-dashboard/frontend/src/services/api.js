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

export const syncGNS3 = async (gns3Url = 'http://127.0.0.1:3080') => {
  const response = await apiClient.post(`/compliance/gns3-sync?gns3_url=${encodeURIComponent(gns3Url)}`);
  return response.data;
};