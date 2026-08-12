import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const fetchComplianceData = async () => {
    const response = await apiClient.get('/compliance');
    return response.data;
};

export const fetchDeviceList = async () => {
    const response = await apiClient.get('/devices');
    return response.data;
};

export const updateDevice = async (deviceId, deviceData) => {
    const response = await apiClient.put(`/devices/${deviceId}`, deviceData);
    return response.data;
};

export const addDevice = async (deviceData) => {
    const response = await apiClient.post('/devices', deviceData);
    return response.data;
};

export const deleteDevice = async (deviceId) => {
    const response = await apiClient.delete(`/devices/${deviceId}`);
    return response.data;
};