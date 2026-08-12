import React, { useEffect, useState } from 'react';
import { fetchDevices } from '../services/api';

const DeviceList = () => {
    const [devices, setDevices] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const getDevices = async () => {
            try {
                const deviceData = await fetchDevices();
                setDevices(deviceData);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        getDevices();
    }, []);

    if (loading) {
        return <div>Loading devices...</div>;
    }

    if (error) {
        return <div>Error fetching devices: {error}</div>;
    }

    return (
        <div>
            <h2>Device List</h2>
            <ul>
                {devices.map(device => (
                    <li key={device.id}>
                        {device.name} - Compliance Status: {device.complianceStatus}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default DeviceList;